"""Calculation API for two-group intervention sample planning.

The module is deliberately dependency-free. It implements the normal
approximations described in the methodology chapter that oriented this app:
two independent means, two independent proportions, finite-population
correction, attrition/nonresponse correction, cluster design effect, and
Bonferroni adjustment for planned primary comparisons.
"""

# File version: 1.0; date: 2026-05-11

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import math
from pathlib import Path
from statistics import NormalDist
from typing import Any


NORMAL = NormalDist()
SUPPORTED_LANGUAGES = {"en", "pt"}
SUPPORTED_OUTCOMES = {"continuous", "binary"}
SUPPORTED_ALTERNATIVES = {"two_sided", "greater", "less"}


@dataclass(slots=True)
class StudyConfig:
    """All inputs needed to plan a two-group intervention experiment.

    Rates are represented as proportions from 0 to 1. For example, 80% is
    stored as ``0.80``.
    """

    study_name: str = "Untitled intervention study"
    language: str = "en"
    analysis_unit: str = "person"
    observation_unit: str = "person"
    outcome_type: str = "continuous"
    alternative: str = "two_sided"
    alpha: float = 0.05
    power: float = 0.80
    primary_comparisons: int = 1
    allocation_ratio: float = 1.0  # intervention/control

    effect_size_d: float | None = 0.50
    mean_control: float | None = None
    mean_intervention: float | None = None
    sd_pooled: float | None = None

    proportion_control: float = 0.45
    proportion_intervention: float = 0.60

    apply_fpc: bool = False
    finite_population: int | None = None
    cluster_average_size: float = 1.0
    intraclass_correlation: float = 0.0

    response_rate: float = 1.0
    completion_rate: float = 1.0
    usable_data_rate: float = 1.0
    extra_buffer_rate: float = 0.0

    intervention_label: str = "Intervention"
    control_label: str = "Control"
    notes: str = ""


@dataclass(slots=True)
class GroupSizes:
    """Group sizes for one planning stage."""

    control: int
    intervention: int

    @property
    def total(self) -> int:
        return self.control + self.intervention


@dataclass(slots=True)
class SensitivityRow:
    """One sample-size scenario in the sensitivity table."""

    label: str
    control: int
    intervention: int
    total: int
    invited_total: int


@dataclass(slots=True)
class SamplePlan:
    """Computed sample-size plan and explanatory details."""

    config: StudyConfig
    alpha_adjusted: float
    z_alpha: float
    z_power: float
    effect_size_used: float
    design_effect: float
    finite_population_applied: bool
    effective_data_rate: float
    initial_valid: GroupSizes
    fpc_adjusted_valid: GroupSizes
    design_adjusted_valid: GroupSizes
    assigned_needed: GroupSizes
    invited_needed: GroupSizes
    achieved_power_at_valid_target: float
    method: str
    formulas: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    sensitivity: list[SensitivityRow] = field(default_factory=list)


class PlanningError(ValueError):
    """Raised when a configuration cannot produce a meaningful plan."""


def config_to_dict(config: StudyConfig) -> dict[str, Any]:
    return asdict(config)


def config_from_dict(data: dict[str, Any]) -> StudyConfig:
    valid_fields = StudyConfig.__dataclass_fields__.keys()
    cleaned = {key: value for key, value in data.items() if key in valid_fields}
    return StudyConfig(**cleaned)


def save_config(config: StudyConfig, path: str | Path) -> None:
    target = Path(path)
    target.write_text(json.dumps(config_to_dict(config), indent=2), encoding="utf-8")


def load_config(path: str | Path) -> StudyConfig:
    source = Path(path)
    return config_from_dict(json.loads(source.read_text(encoding="utf-8")))


def calculate_plan(config: StudyConfig) -> SamplePlan:
    """Calculate all sample-size stages for a two-group intervention study."""

    _validate_config(config)
    alpha_adjusted = config.alpha / config.primary_comparisons
    z_alpha = _z_alpha(alpha_adjusted, config.alternative)
    z_power = NORMAL.inv_cdf(config.power)
    effect_size = _effect_size(config)

    if config.outcome_type == "continuous":
        initial_valid, method, formulas = _continuous_initial(config, z_alpha, z_power, effect_size)
    elif config.outcome_type == "binary":
        initial_valid, method, formulas = _binary_initial(config, z_alpha, z_power)
    else:
        raise PlanningError(f"Unsupported outcome type: {config.outcome_type}")

    warnings = _base_warnings(config, alpha_adjusted, effect_size)
    fpc_adjusted, fpc_applied = _apply_fpc(initial_valid, config)
    design_effect = _design_effect(config)
    design_adjusted = _inflate_groups(fpc_adjusted, design_effect)
    assigned_needed, invited_needed, effective_data_rate = _correct_for_missing_data(design_adjusted, config)
    achieved_power = _achieved_power(config, design_adjusted, z_alpha, effect_size)
    sensitivity = _build_sensitivity(config)

    if config.finite_population and invited_needed.total > config.finite_population:
        warnings.append(
            "The invited/recruited target is larger than the finite population you entered."
        )
    if effective_data_rate < 0.50:
        warnings.append(
            "The effective data rate is below 50%; recruitment planning is more fragile."
        )
    if config.allocation_ratio < 0.5 or config.allocation_ratio > 2.0:
        warnings.append(
            "The groups are strongly unbalanced; this usually increases total sample size."
        )
    if design_effect > 1.5:
        warnings.append(
            "Cluster correction substantially increased the sample; adding clusters may help more than adding people inside the same cluster."
        )

    return SamplePlan(
        config=config,
        alpha_adjusted=alpha_adjusted,
        z_alpha=z_alpha,
        z_power=z_power,
        effect_size_used=effect_size,
        design_effect=design_effect,
        finite_population_applied=fpc_applied,
        effective_data_rate=effective_data_rate,
        initial_valid=initial_valid,
        fpc_adjusted_valid=fpc_adjusted,
        design_adjusted_valid=design_adjusted,
        assigned_needed=assigned_needed,
        invited_needed=invited_needed,
        achieved_power_at_valid_target=achieved_power,
        method=method,
        formulas=formulas,
        warnings=warnings,
        sensitivity=sensitivity,
    )


def render_report(plan: SamplePlan, language: str | None = None) -> str:
    """Render a concise bilingual-friendly plain text report."""

    lang = language or plan.config.language
    return _render_pt(plan) if lang == "pt" else _render_en(plan)


def _validate_config(config: StudyConfig) -> None:
    if config.language not in SUPPORTED_LANGUAGES:
        raise PlanningError("language must be 'en' or 'pt'.")
    if config.outcome_type not in SUPPORTED_OUTCOMES:
        raise PlanningError("outcome_type must be 'continuous' or 'binary'.")
    if config.alternative not in SUPPORTED_ALTERNATIVES:
        raise PlanningError("alternative must be 'two_sided', 'greater', or 'less'.")
    if not 0 < config.alpha < 1:
        raise PlanningError("alpha must be between 0 and 1.")
    if not 0 < config.power < 1:
        raise PlanningError("power must be between 0 and 1.")
    if config.primary_comparisons < 1:
        raise PlanningError("primary_comparisons must be at least 1.")
    if config.allocation_ratio <= 0:
        raise PlanningError("allocation_ratio must be positive.")
    for name in ("response_rate", "completion_rate", "usable_data_rate"):
        value = getattr(config, name)
        if not 0 < value <= 1:
            raise PlanningError(f"{name} must be in (0, 1].")
    if not 0 <= config.extra_buffer_rate < 1:
        raise PlanningError("extra_buffer_rate must be in [0, 1).")
    if config.cluster_average_size < 1:
        raise PlanningError("cluster_average_size must be at least 1.")
    if config.intraclass_correlation < 0:
        raise PlanningError("intraclass_correlation cannot be negative.")
    if config.apply_fpc:
        if not config.finite_population or config.finite_population <= 0:
            raise PlanningError("finite_population must be positive when apply_fpc is true.")
    if config.outcome_type == "binary":
        for name in ("proportion_control", "proportion_intervention"):
            value = getattr(config, name)
            if not 0 < value < 1:
                raise PlanningError(f"{name} must be between 0 and 1.")


def _z_alpha(alpha: float, alternative: str) -> float:
    tail_area = alpha / 2 if alternative == "two_sided" else alpha
    return NORMAL.inv_cdf(1 - tail_area)


def _effect_size(config: StudyConfig) -> float:
    if config.outcome_type == "continuous":
        if config.effect_size_d and config.effect_size_d > 0:
            return abs(config.effect_size_d)
        if (
            config.mean_control is not None
            and config.mean_intervention is not None
            and config.sd_pooled is not None
            and config.sd_pooled > 0
        ):
            return abs(config.mean_intervention - config.mean_control) / config.sd_pooled
        raise PlanningError(
            "For continuous outcomes, provide effect_size_d or means plus pooled SD."
        )
    return abs(config.proportion_intervention - config.proportion_control)


def _continuous_initial(
    config: StudyConfig, z_alpha: float, z_power: float, effect_size: float
) -> tuple[GroupSizes, str, list[str]]:
    if effect_size <= 0:
        raise PlanningError("effect_size_d must be positive.")
    k = config.allocation_ratio
    n_control = (1 + 1 / k) * (z_alpha + z_power) ** 2 / effect_size**2
    n_intervention = k * n_control
    method = "Normal approximation for two independent means"
    formulas = [
        "d = (mean_intervention - mean_control) / pooled_sd",
        "n_control = (1 + 1/k) * (z_alpha + z_power)^2 / d^2",
        "n_intervention = k * n_control",
    ]
    return GroupSizes(math.ceil(n_control), math.ceil(n_intervention)), method, formulas


def _binary_initial(
    config: StudyConfig, z_alpha: float, z_power: float
) -> tuple[GroupSizes, str, list[str]]:
    p_control = config.proportion_control
    p_intervention = config.proportion_intervention
    diff = abs(p_intervention - p_control)
    if diff <= 0:
        raise PlanningError("proportion_intervention and proportion_control must differ.")
    k = config.allocation_ratio
    p_bar = (p_control + p_intervention) / 2
    pooled = (1 + 1 / k) * p_bar * (1 - p_bar)
    unpooled = p_control * (1 - p_control) + (p_intervention * (1 - p_intervention) / k)
    n_control = ((z_alpha * math.sqrt(pooled) + z_power * math.sqrt(unpooled)) ** 2) / diff**2
    n_intervention = k * n_control
    method = "Normal approximation for two independent proportions"
    formulas = [
        "p_bar = (p_control + p_intervention) / 2",
        "n_control = [z_alpha*sqrt((1+1/k)*p_bar*(1-p_bar)) + z_power*sqrt(p_c*(1-p_c)+p_i*(1-p_i)/k)]^2 / (p_i-p_c)^2",
        "n_intervention = k * n_control",
    ]
    return GroupSizes(math.ceil(n_control), math.ceil(n_intervention)), method, formulas


def _apply_fpc(groups: GroupSizes, config: StudyConfig) -> tuple[GroupSizes, bool]:
    if not config.apply_fpc or not config.finite_population:
        return groups, False
    total = groups.total
    adjusted_total = (config.finite_population * total) / (config.finite_population + total - 1)
    return _allocate_total(math.ceil(adjusted_total), config.allocation_ratio), True


def _design_effect(config: StudyConfig) -> float:
    if config.cluster_average_size <= 1 or config.intraclass_correlation <= 0:
        return 1.0
    return 1 + (config.cluster_average_size - 1) * config.intraclass_correlation


def _inflate_groups(groups: GroupSizes, multiplier: float) -> GroupSizes:
    return GroupSizes(math.ceil(groups.control * multiplier), math.ceil(groups.intervention * multiplier))


def _correct_for_missing_data(
    groups: GroupSizes, config: StudyConfig
) -> tuple[GroupSizes, GroupSizes, float]:
    completion_factor = (
        config.completion_rate
        * config.usable_data_rate
        * (1 - config.extra_buffer_rate)
    )
    if completion_factor <= 0:
        raise PlanningError("completion, usable-data, and buffer rates make collection impossible.")
    assigned = GroupSizes(
        math.ceil(groups.control / completion_factor),
        math.ceil(groups.intervention / completion_factor),
    )
    invited = GroupSizes(
        math.ceil(assigned.control / config.response_rate),
        math.ceil(assigned.intervention / config.response_rate),
    )
    effective_data_rate = config.response_rate * completion_factor
    return assigned, invited, effective_data_rate


def _allocate_total(total: int, ratio: float) -> GroupSizes:
    control = math.ceil(total / (1 + ratio))
    intervention = math.ceil(total * ratio / (1 + ratio))
    return GroupSizes(control, intervention)


def _achieved_power(
    config: StudyConfig, groups: GroupSizes, z_alpha: float, effect_size: float
) -> float:
    k_observed = groups.intervention / groups.control
    if config.outcome_type == "continuous":
        z_beta = math.sqrt(groups.control / (1 + 1 / k_observed)) * effect_size - z_alpha
        return _clamp(NORMAL.cdf(z_beta), 0.0, 1.0)

    p_control = config.proportion_control
    p_intervention = config.proportion_intervention
    diff = abs(p_intervention - p_control)
    p_bar = (p_control + p_intervention) / 2
    pooled = (1 + 1 / k_observed) * p_bar * (1 - p_bar)
    unpooled = p_control * (1 - p_control) + p_intervention * (1 - p_intervention) / k_observed
    z_beta = (math.sqrt(groups.control) * diff - z_alpha * math.sqrt(pooled)) / math.sqrt(unpooled)
    return _clamp(NORMAL.cdf(z_beta), 0.0, 1.0)


def _base_warnings(config: StudyConfig, alpha_adjusted: float, effect_size: float) -> list[str]:
    warnings: list[str] = []
    if config.primary_comparisons > 1:
        warnings.append(
            f"Alpha was adjusted by Bonferroni for {config.primary_comparisons} planned primary comparisons: {alpha_adjusted:.5f}."
        )
    if config.outcome_type == "continuous" and effect_size < 0.20:
        warnings.append("The requested standardized effect is very small; the sample may become large.")
    if config.outcome_type == "binary" and effect_size < 0.05:
        warnings.append("The requested difference in proportions is small; the sample may become large.")
    if config.apply_fpc:
        warnings.append(
            "Finite-population correction is appropriate only when the inference is restricted to the closed population entered here."
        )
    return warnings


def _build_sensitivity(config: StudyConfig) -> list[SensitivityRow]:
    rows: list[SensitivityRow] = []
    variants: list[tuple[str, StudyConfig]] = []

    if config.outcome_type == "continuous":
        base = _effect_size(config)
        for multiplier in (0.8, 1.0, 1.2):
            variant = config_from_dict(config_to_dict(config))
            variant.effect_size_d = max(base * multiplier, 1e-9)
            variants.append((f"effect x {multiplier:.1f}", variant))
    else:
        p0 = config.proportion_control
        diff = config.proportion_intervention - config.proportion_control
        for multiplier in (0.8, 1.0, 1.2):
            variant = config_from_dict(config_to_dict(config))
            variant.proportion_intervention = _clamp(p0 + diff * multiplier, 0.001, 0.999)
            variants.append((f"difference x {multiplier:.1f}", variant))

    for desired_power in (0.80, 0.90, 0.95):
        if abs(config.power - desired_power) > 0.0001:
            variant = config_from_dict(config_to_dict(config))
            variant.power = desired_power
            variants.append((f"power {desired_power:.0%}", variant))

    for label, variant in variants:
        plan = _calculate_no_sensitivity(variant)
        rows.append(
            SensitivityRow(
                label=label,
                control=plan.design_adjusted_valid.control,
                intervention=plan.design_adjusted_valid.intervention,
                total=plan.design_adjusted_valid.total,
                invited_total=plan.invited_needed.total,
            )
        )
    return rows


def _calculate_no_sensitivity(config: StudyConfig) -> SamplePlan:
    """Internal calculation without recursive sensitivity generation."""

    _validate_config(config)
    alpha_adjusted = config.alpha / config.primary_comparisons
    z_alpha = _z_alpha(alpha_adjusted, config.alternative)
    z_power = NORMAL.inv_cdf(config.power)
    effect_size = _effect_size(config)
    if config.outcome_type == "continuous":
        initial_valid, method, formulas = _continuous_initial(config, z_alpha, z_power, effect_size)
    else:
        initial_valid, method, formulas = _binary_initial(config, z_alpha, z_power)
    warnings = _base_warnings(config, alpha_adjusted, effect_size)
    fpc_adjusted, fpc_applied = _apply_fpc(initial_valid, config)
    design_effect = _design_effect(config)
    design_adjusted = _inflate_groups(fpc_adjusted, design_effect)
    assigned_needed, invited_needed, effective_data_rate = _correct_for_missing_data(design_adjusted, config)
    achieved_power = _achieved_power(config, design_adjusted, z_alpha, effect_size)
    return SamplePlan(
        config=config,
        alpha_adjusted=alpha_adjusted,
        z_alpha=z_alpha,
        z_power=z_power,
        effect_size_used=effect_size,
        design_effect=design_effect,
        finite_population_applied=fpc_applied,
        effective_data_rate=effective_data_rate,
        initial_valid=initial_valid,
        fpc_adjusted_valid=fpc_adjusted,
        design_adjusted_valid=design_adjusted,
        assigned_needed=assigned_needed,
        invited_needed=invited_needed,
        achieved_power_at_valid_target=achieved_power,
        method=method,
        formulas=formulas,
        warnings=warnings,
        sensitivity=[],
    )


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _render_en(plan: SamplePlan) -> str:
    c = plan.config
    lines = [
        f"Study: {c.study_name}",
        f"Method: {plan.method}",
        "",
        "Main result",
        f"- Initial valid data target, assuming everyone provides usable data: {plan.initial_valid.control} {c.control_label} + {plan.initial_valid.intervention} {c.intervention_label} = {plan.initial_valid.total}.",
        f"- Valid data target after finite-population and cluster/design corrections: {plan.design_adjusted_valid.control} {c.control_label} + {plan.design_adjusted_valid.intervention} {c.intervention_label} = {plan.design_adjusted_valid.total}.",
        f"- Participants to assign/start after completion and usable-data corrections: {plan.assigned_needed.control} {c.control_label} + {plan.assigned_needed.intervention} {c.intervention_label} = {plan.assigned_needed.total}.",
        f"- People to invite/contact after response-rate correction: {plan.invited_needed.control} {c.control_label} + {plan.invited_needed.intervention} {c.intervention_label} = {plan.invited_needed.total}.",
        "",
        "Inputs used",
        f"- alpha: {c.alpha:.4f}; adjusted alpha: {plan.alpha_adjusted:.4f}; target power: {c.power:.1%}; achieved power at valid target: {plan.achieved_power_at_valid_target:.1%}.",
        f"- allocation ratio: {c.intervention_label}/{c.control_label} = {c.allocation_ratio:g}; effective data rate: {plan.effective_data_rate:.1%}; design effect: {plan.design_effect:.3f}.",
        f"- effect value used: {plan.effect_size_used:.4f}.",
        "",
        "Justification paragraph",
        (
            f"The experiment was planned as a two-group comparison between {c.intervention_label} and {c.control_label}. "
            f"The sample size was calculated for a {c.outcome_type} outcome using {plan.method.lower()}, "
            f"with alpha={plan.alpha_adjusted:.4f}, target power={c.power:.1%}, allocation ratio={c.allocation_ratio:g}, "
            f"and effect value {plan.effect_size_used:.4f}. The initial analyzable target was {plan.initial_valid.total} units. "
            f"After design and data-availability corrections, the study should aim for {plan.design_adjusted_valid.total} valid analyzable units, "
            f"assign/start about {plan.assigned_needed.total}, and invite/contact about {plan.invited_needed.total} people."
        ),
    ]
    if plan.warnings:
        lines.extend(["", "Warnings"])
        lines.extend(f"- {warning}" for warning in plan.warnings)
    lines.extend(["", "Formulas"])
    lines.extend(f"- {formula}" for formula in plan.formulas)
    return "\n".join(lines)


def _render_pt(plan: SamplePlan) -> str:
    c = plan.config
    outcome = "contínuo" if c.outcome_type == "continuous" else "binário"
    lines = [
        f"Estudo: {c.study_name}",
        f"Método: {plan.method}",
        "",
        "Resultado principal",
        f"- Alvo inicial de dados válidos, supondo que todas as pessoas forneçam dados utilizáveis: {plan.initial_valid.control} {c.control_label} + {plan.initial_valid.intervention} {c.intervention_label} = {plan.initial_valid.total}.",
        f"- Alvo de dados válidos após correções de população finita e desenho/cluster: {plan.design_adjusted_valid.control} {c.control_label} + {plan.design_adjusted_valid.intervention} {c.intervention_label} = {plan.design_adjusted_valid.total}.",
        f"- Participantes a alocar/iniciar após correções de conclusão e dados utilizáveis: {plan.assigned_needed.control} {c.control_label} + {plan.assigned_needed.intervention} {c.intervention_label} = {plan.assigned_needed.total}.",
        f"- Pessoas a convidar/contatar após correção pela taxa de resposta: {plan.invited_needed.control} {c.control_label} + {plan.invited_needed.intervention} {c.intervention_label} = {plan.invited_needed.total}.",
        "",
        "Entradas usadas",
        f"- alfa: {c.alpha:.4f}; alfa ajustado: {plan.alpha_adjusted:.4f}; poder desejado: {c.power:.1%}; poder aproximado no alvo válido: {plan.achieved_power_at_valid_target:.1%}.",
        f"- razão de alocação: {c.intervention_label}/{c.control_label} = {c.allocation_ratio:g}; taxa efetiva de dados: {plan.effective_data_rate:.1%}; efeito de desenho: {plan.design_effect:.3f}.",
        f"- valor de efeito usado: {plan.effect_size_used:.4f}.",
        "",
        "Parágrafo de justificativa",
        (
            f"O experimento foi planejado como comparação entre dois grupos, {c.intervention_label} e {c.control_label}. "
            f"O tamanho amostral foi calculado para um desfecho {outcome}, usando {plan.method.lower()}, "
            f"com alfa={plan.alpha_adjusted:.4f}, poder desejado de {c.power:.1%}, razão de alocação={c.allocation_ratio:g} "
            f"e valor de efeito {plan.effect_size_used:.4f}. O alvo inicial de unidades analisáveis foi {plan.initial_valid.total}. "
            f"Após correções de desenho e disponibilidade dos dados, o estudo deve buscar {plan.design_adjusted_valid.total} unidades analisáveis válidas, "
            f"alocar/iniciar cerca de {plan.assigned_needed.total} participantes e convidar/contatar cerca de {plan.invited_needed.total} pessoas."
        ),
    ]
    if plan.warnings:
        lines.extend(["", "Avisos"])
        lines.extend(f"- {warning}" for warning in plan.warnings)
    lines.extend(["", "Fórmulas"])
    lines.extend(f"- {formula}" for formula in plan.formulas)
    return "\n".join(lines)
