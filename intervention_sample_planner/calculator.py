"""Calculation API for intervention-study planning and result evaluation."""

# File version: 2.0; date: 2026-05-11

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
SUPPORTED_STUDY_DESIGNS = {
    "parallel_two_group",
    "pretest_posttest_control",
    "one_group_pre_post",
}
SUPPORTED_ANALYSIS_MODES = {"plan", "evaluate"}


@dataclass(slots=True)
class StudyConfig:
    """Inputs for planning or evaluating an intervention study."""

    study_name: str = "Untitled intervention study"
    language: str = "en"
    study_design: str = "parallel_two_group"
    analysis_mode: str = "plan"
    analysis_unit: str = "person"
    observation_unit: str = "person"
    outcome_type: str = "continuous"
    alternative: str = "two_sided"
    alpha: float = 0.05
    power: float = 0.80
    primary_comparisons: int = 1
    allocation_ratio: float = 1.0

    effect_size_d: float | None = 0.50
    mean_control: float | None = None
    mean_intervention: float | None = None
    sd_pooled: float | None = None
    pre_post_correlation: float = 0.50

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

    observed_control_n: int | None = None
    observed_intervention_n: int | None = None
    observed_total_n: int | None = None
    observed_effect_size: float | None = None

    intervention_label: str = "Intervention"
    control_label: str = "Control"
    notes: str = ""
    range_override_fields: list[str] = field(default_factory=list)


@dataclass(slots=True)
class GroupSizes:
    control: int
    intervention: int

    @property
    def total(self) -> int:
        return self.control + self.intervention


@dataclass(slots=True)
class SensitivityRow:
    label: str
    control: int
    intervention: int
    total: int
    invited_total: int


@dataclass(slots=True)
class ObservedAnalysis:
    observed_control: int
    observed_intervention: int
    observed_total: int
    observed_effect_size: float
    z_statistic: float
    p_value: float
    achieved_power: float
    method: str


@dataclass(slots=True)
class SamplePlan:
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
    suggestions: list[str] = field(default_factory=list)
    sensitivity: list[SensitivityRow] = field(default_factory=list)
    observed_analysis: ObservedAnalysis | None = None


class PlanningError(ValueError):
    """Raised when the configuration is not adequate for the requested run."""


def config_to_dict(config: StudyConfig) -> dict[str, Any]:
    return asdict(config)


def config_from_dict(data: dict[str, Any]) -> StudyConfig:
    valid_fields = StudyConfig.__dataclass_fields__.keys()
    cleaned = {key: value for key, value in data.items() if key in valid_fields}
    return StudyConfig(**cleaned)


def save_config(config: StudyConfig, path: str | Path) -> None:
    target = Path(path)
    payload = config_to_dict(config)
    payload.setdefault("_file_version", "2.0")
    payload.setdefault("_file_date", "2026-05-11")
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def load_config(path: str | Path) -> StudyConfig:
    source = Path(path)
    return config_from_dict(json.loads(source.read_text(encoding="utf-8")))


def calculate_plan(config: StudyConfig) -> SamplePlan:
    _validate_config(config)
    alpha_adjusted = config.alpha / config.primary_comparisons
    z_alpha = _z_alpha(alpha_adjusted, config.alternative)
    z_power = NORMAL.inv_cdf(config.power)

    effect_size = _planned_effect_size(config) if config.analysis_mode == "plan" else 0.0
    initial_valid = GroupSizes(0, 0)
    fpc_adjusted = GroupSizes(0, 0)
    design_adjusted = GroupSizes(0, 0)
    assigned_needed = GroupSizes(0, 0)
    invited_needed = GroupSizes(0, 0)
    design_effect = _design_effect(config)
    effective_data_rate = (
        config.response_rate * config.completion_rate * config.usable_data_rate * (1 - config.extra_buffer_rate)
    )
    method = _method_label(config)
    formulas: list[str] = []
    achieved_power = 0.0
    fpc_applied = False
    warnings: list[str] = []

    if config.analysis_mode == "plan":
        initial_valid, method, formulas = _initial_valid_sample(config, z_alpha, z_power, effect_size)
        warnings.extend(_base_warnings(config, alpha_adjusted, effect_size))
        fpc_adjusted, fpc_applied = _apply_fpc(initial_valid, config)
        design_adjusted = _inflate_groups(fpc_adjusted, design_effect)
        assigned_needed, invited_needed, effective_data_rate = _correct_for_missing_data(design_adjusted, config)
        achieved_power = _achieved_power(config, design_adjusted, z_alpha, effect_size)

    observed_analysis = _observed_analysis(config, z_alpha)
    suggestions = _build_suggestions(config, initial_valid, design_adjusted, observed_analysis)
    sensitivity = _build_sensitivity(config) if config.analysis_mode == "plan" else []

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
        suggestions=suggestions,
        sensitivity=sensitivity,
        observed_analysis=observed_analysis,
    )


def render_report(plan: SamplePlan, language: str | None = None) -> str:
    lang = language or plan.config.language
    return _render_pt(plan) if lang == "pt" else _render_en(plan)


def _validate_config(config: StudyConfig) -> None:
    if config.language not in SUPPORTED_LANGUAGES:
        raise PlanningError("language must be 'en' or 'pt'.")
    if config.study_design not in SUPPORTED_STUDY_DESIGNS:
        raise PlanningError("Unsupported study_design.")
    if config.analysis_mode not in SUPPORTED_ANALYSIS_MODES:
        raise PlanningError("analysis_mode must be 'plan' or 'evaluate'.")
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
    if not 0 <= config.pre_post_correlation < 1:
        raise PlanningError("pre_post_correlation must be in [0, 1).")
    for name in ("response_rate", "completion_rate", "usable_data_rate"):
        value = getattr(config, name)
        if not 0 < value <= 1:
            raise PlanningError(f"{name} must be in (0, 1].")
    if not 0 <= config.extra_buffer_rate < 1:
        raise PlanningError("extra_buffer_rate must be in [0, 1).")
    if config.cluster_average_size < 1:
        raise PlanningError("cluster_average_size must be at least 1.")
    if not 0 <= config.intraclass_correlation < 1:
        raise PlanningError("intraclass_correlation must be in [0, 1).")
    if config.apply_fpc and (not config.finite_population or config.finite_population <= 0):
        raise PlanningError("finite_population must be positive when apply_fpc is true.")

    if config.study_design != "parallel_two_group" and config.outcome_type == "binary":
        raise PlanningError(
            "Binary outcomes are currently supported only for the two independent groups path."
        )

    if config.analysis_mode == "plan":
        if config.study_design == "parallel_two_group" and config.outcome_type == "binary":
            for name in ("proportion_control", "proportion_intervention"):
                value = getattr(config, name)
                if not 0 < value < 1:
                    raise PlanningError(f"{name} must be between 0 and 1.")
        else:
            _planned_effect_size(config)

    if config.analysis_mode == "evaluate":
        _validate_observed_inputs(config)


def _validate_observed_inputs(config: StudyConfig) -> None:
    if config.study_design == "one_group_pre_post":
        if not config.observed_total_n or config.observed_total_n <= 1:
            raise PlanningError("observed_total_n must be at least 2 in achieved-result mode.")
    else:
        if not config.observed_control_n or not config.observed_intervention_n:
            raise PlanningError(
                "observed_control_n and observed_intervention_n are required in achieved-result mode."
            )
        if config.observed_control_n <= 1 or config.observed_intervention_n <= 1:
            raise PlanningError("Observed group sizes must be at least 2.")
    if config.observed_effect_size is None:
        raise PlanningError("observed_effect_size is required in achieved-result mode.")
    if config.study_design == "parallel_two_group" and config.outcome_type == "binary":
        if not 0 < abs(config.observed_effect_size) < 1:
            raise PlanningError("For binary achieved-result mode, observed_effect_size must be a proportion difference.")
    elif config.observed_effect_size == 0:
        raise PlanningError("observed_effect_size cannot be zero in achieved-result mode.")


def _z_alpha(alpha: float, alternative: str) -> float:
    tail_area = alpha / 2 if alternative == "two_sided" else alpha
    return NORMAL.inv_cdf(1 - tail_area)


def _planned_effect_size(config: StudyConfig) -> float:
    if config.study_design == "parallel_two_group" and config.outcome_type == "binary":
        diff = abs(config.proportion_intervention - config.proportion_control)
        if diff <= 0:
            raise PlanningError("proportion_intervention and proportion_control must differ.")
        return diff
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
        "Provide effect_size_d or means plus pooled SD for the selected continuous design."
    )


def _initial_valid_sample(
    config: StudyConfig, z_alpha: float, z_power: float, effect_size: float
) -> tuple[GroupSizes, str, list[str]]:
    if config.study_design == "parallel_two_group":
        if config.outcome_type == "continuous":
            return _parallel_continuous_initial(config, z_alpha, z_power, effect_size)
        return _parallel_binary_initial(config, z_alpha, z_power)
    if config.study_design == "pretest_posttest_control":
        return _pretest_posttest_control_initial(config, z_alpha, z_power, effect_size)
    return _one_group_pre_post_initial(config, z_alpha, z_power, effect_size)


def _parallel_continuous_initial(
    config: StudyConfig, z_alpha: float, z_power: float, effect_size: float
) -> tuple[GroupSizes, str, list[str]]:
    if effect_size <= 0:
        raise PlanningError("effect_size_d must be positive.")
    k = config.allocation_ratio
    n_control = (1 + 1 / k) * (z_alpha + z_power) ** 2 / effect_size**2
    n_intervention = k * n_control
    formulas = [
        "d = (mean_intervention - mean_control) / pooled_sd",
        "n_control = (1 + 1/k) * (z_alpha + z_power)^2 / d^2",
        "n_intervention = k * n_control",
    ]
    return (
        GroupSizes(math.ceil(n_control), math.ceil(n_intervention)),
        "Normal approximation for two independent means",
        formulas,
    )


def _parallel_binary_initial(
    config: StudyConfig, z_alpha: float, z_power: float
) -> tuple[GroupSizes, str, list[str]]:
    p_control = config.proportion_control
    p_intervention = config.proportion_intervention
    diff = abs(p_intervention - p_control)
    k = config.allocation_ratio
    p_bar = (p_control + p_intervention) / 2
    pooled = (1 + 1 / k) * p_bar * (1 - p_bar)
    unpooled = p_control * (1 - p_control) + (p_intervention * (1 - p_intervention) / k)
    n_control = ((z_alpha * math.sqrt(pooled) + z_power * math.sqrt(unpooled)) ** 2) / diff**2
    n_intervention = k * n_control
    formulas = [
        "p_bar = (p_control + p_intervention) / 2",
        "n_control = [z_alpha*sqrt((1+1/k)*p_bar*(1-p_bar)) + z_power*sqrt(p_c*(1-p_c)+p_i*(1-p_i)/k)]^2 / (p_i-p_c)^2",
        "n_intervention = k * n_control",
    ]
    return (
        GroupSizes(math.ceil(n_control), math.ceil(n_intervention)),
        "Normal approximation for two independent proportions",
        formulas,
    )


def _pretest_posttest_control_initial(
    config: StudyConfig, z_alpha: float, z_power: float, effect_size: float
) -> tuple[GroupSizes, str, list[str]]:
    if effect_size <= 0:
        raise PlanningError("effect_size_d must be positive.")
    k = config.allocation_ratio
    base_control = (1 + 1 / k) * (z_alpha + z_power) ** 2 / effect_size**2
    adjustment = max(0.05, 1 - config.pre_post_correlation**2)
    n_control = base_control * adjustment
    n_intervention = k * n_control
    formulas = [
        "Start from the two-group continuous approximation on the target standardized effect.",
        "Apply ANCOVA-style precision gain with factor (1 - r^2), where r is the pre/post correlation.",
        "n_control_adjusted = n_control_parallel * (1 - r^2)",
    ]
    return (
        GroupSizes(math.ceil(n_control), math.ceil(n_intervention)),
        "Approximate pre-test/post-test with control (ANCOVA-style precision adjustment)",
        formulas,
    )


def _one_group_pre_post_initial(
    config: StudyConfig, z_alpha: float, z_power: float, effect_size: float
) -> tuple[GroupSizes, str, list[str]]:
    if effect_size <= 0:
        raise PlanningError("effect_size_d must be positive.")
    n_total = ((z_alpha + z_power) ** 2) / effect_size**2
    formulas = [
        "d_change = mean_change / sd_change",
        "n = (z_alpha + z_power)^2 / d_change^2",
        "Completion should mean providing both the pre-test and the post-test.",
    ]
    return (
        GroupSizes(0, math.ceil(n_total)),
        "Approximate one-group pre-test/post-test for standardized mean change",
        formulas,
    )


def _apply_fpc(groups: GroupSizes, config: StudyConfig) -> tuple[GroupSizes, bool]:
    if not config.apply_fpc or not config.finite_population:
        return groups, False
    total = groups.total
    adjusted_total = (config.finite_population * total) / (config.finite_population + total - 1)
    return _allocate_total(math.ceil(adjusted_total), config), True


def _allocate_total(total: int, config: StudyConfig) -> GroupSizes:
    if config.study_design == "one_group_pre_post":
        return GroupSizes(0, total)
    control = math.ceil(total / (1 + config.allocation_ratio))
    intervention = math.ceil(total * config.allocation_ratio / (1 + config.allocation_ratio))
    return GroupSizes(control, intervention)


def _design_effect(config: StudyConfig) -> float:
    if config.cluster_average_size <= 1 or config.intraclass_correlation <= 0:
        return 1.0
    return 1 + (config.cluster_average_size - 1) * config.intraclass_correlation


def _inflate_groups(groups: GroupSizes, multiplier: float) -> GroupSizes:
    return GroupSizes(
        math.ceil(groups.control * multiplier),
        math.ceil(groups.intervention * multiplier),
    )


def _correct_for_missing_data(
    groups: GroupSizes, config: StudyConfig
) -> tuple[GroupSizes, GroupSizes, float]:
    completion_factor = (
        config.completion_rate * config.usable_data_rate * (1 - config.extra_buffer_rate)
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
    return assigned, invited, config.response_rate * completion_factor


def _achieved_power(
    config: StudyConfig, groups: GroupSizes, z_alpha: float, effect_size: float
) -> float:
    if groups.total <= 0 or effect_size <= 0:
        return 0.0
    if config.study_design == "one_group_pre_post":
        z_beta = math.sqrt(groups.total) * effect_size - z_alpha
        return _clamp(NORMAL.cdf(z_beta), 0.0, 1.0)
    if config.study_design == "pretest_posttest_control":
        k_observed = max(groups.intervention, 1) / max(groups.control, 1)
        base = math.sqrt(groups.control / (1 + 1 / k_observed))
        efficiency_gain = 1 / math.sqrt(max(0.05, 1 - config.pre_post_correlation**2))
        z_beta = base * effect_size * efficiency_gain - z_alpha
        return _clamp(NORMAL.cdf(z_beta), 0.0, 1.0)
    k_observed = max(groups.intervention, 1) / max(groups.control, 1)
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


def _observed_analysis(config: StudyConfig, z_alpha: float) -> ObservedAnalysis | None:
    if config.analysis_mode != "evaluate":
        return None
    effect = abs(config.observed_effect_size or 0.0)
    if config.study_design == "one_group_pre_post":
        n_total = int(config.observed_total_n or 0)
        z_stat = effect * math.sqrt(n_total)
        return ObservedAnalysis(
            observed_control=0,
            observed_intervention=n_total,
            observed_total=n_total,
            observed_effect_size=effect,
            z_statistic=z_stat,
            p_value=_p_value(z_stat, config.alternative),
            achieved_power=_clamp(NORMAL.cdf(z_stat - z_alpha), 0.0, 1.0),
            method="Approximate paired standardized-mean-change evaluation",
        )
    control = int(config.observed_control_n or 0)
    intervention = int(config.observed_intervention_n or 0)
    total = control + intervention
    k = intervention / control
    if config.study_design == "pretest_posttest_control":
        base = math.sqrt(control / (1 + 1 / k))
        efficiency_gain = 1 / math.sqrt(max(0.05, 1 - config.pre_post_correlation**2))
        z_stat = effect * base * efficiency_gain
        method = "Approximate pre-test/post-test with control evaluation"
    elif config.outcome_type == "continuous":
        z_stat = effect * math.sqrt(control / (1 + 1 / k))
        method = "Approximate two-group continuous evaluation"
    else:
        p0 = config.proportion_control
        p1 = _clamp(p0 + effect, 0.001, 0.999)
        p_bar = (p0 + p1) / 2
        pooled = (1 + 1 / k) * p_bar * (1 - p_bar)
        z_stat = math.sqrt(control) * effect / math.sqrt(pooled)
        method = "Approximate two-group proportion-difference evaluation"
    return ObservedAnalysis(
        observed_control=control,
        observed_intervention=intervention,
        observed_total=total,
        observed_effect_size=effect,
        z_statistic=z_stat,
        p_value=_p_value(z_stat, config.alternative),
        achieved_power=_clamp(NORMAL.cdf(z_stat - z_alpha), 0.0, 1.0),
        method=method,
    )


def _p_value(z_stat: float, alternative: str) -> float:
    if alternative == "two_sided":
        return 2 * (1 - NORMAL.cdf(abs(z_stat)))
    return 1 - NORMAL.cdf(abs(z_stat))


def _base_warnings(config: StudyConfig, alpha_adjusted: float, effect_size: float) -> list[str]:
    warnings: list[str] = []
    if config.primary_comparisons > 1:
        warnings.append(
            f"Alpha was adjusted for {config.primary_comparisons} primary comparisons: {alpha_adjusted:.5f}."
        )
    if config.study_design == "one_group_pre_post":
        warnings.append(
            "One-group pre-test/post-test studies are vulnerable to history, maturation, and testing effects because there is no control group."
        )
    if config.study_design == "pretest_posttest_control":
        warnings.append(
            "The pre/post with control path uses an approximation based on the pre/post correlation. Use pilot data or prior studies when possible."
        )
    if config.study_design == "parallel_two_group" and config.outcome_type == "continuous" and effect_size < 0.20:
        warnings.append("The requested standardized effect is very small; the sample may become large.")
    if config.study_design == "parallel_two_group" and config.outcome_type == "binary" and effect_size < 0.05:
        warnings.append("The requested difference in proportions is small; the sample may become large.")
    if config.apply_fpc:
        warnings.append(
            "Finite-population correction is appropriate only when the inference is restricted to the closed population entered here."
        )
    return warnings


def _build_suggestions(
    config: StudyConfig,
    initial_valid: GroupSizes,
    design_adjusted: GroupSizes,
    observed_analysis: ObservedAnalysis | None,
) -> list[str]:
    suggestions: list[str] = []
    if config.study_design == "parallel_two_group":
        suggestions.append(
            "Use the two-group path when the research claim is about a difference between intervention and control."
        )
    elif config.study_design == "pretest_posttest_control":
        suggestions.append(
            "This path is a good fit when a game-based activity is compared with a lesson-only condition and both groups complete pre-test and post-test."
        )
        suggestions.append(
            "Define completion as finishing both tests, not only attending the intervention session."
        )
    else:
        suggestions.append(
            "Without a control group, interpret improvement cautiously: learning gains may reflect practice, maturation, or ordinary instruction."
        )
        suggestions.append(
            "If possible, add a control group in a later study or replicate the result in a second cohort."
        )
    if config.cluster_average_size > 1 and config.intraclass_correlation > 0:
        suggestions.append(
            "Because participants are clustered, adding more clusters may help more than adding more people inside the same cluster."
        )
    if config.response_rate < 0.5:
        suggestions.append(
            "The expected response rate is low. Consider stronger recruitment, reminders, or scheduling support before only inflating the sample."
        )
    if config.completion_rate < 0.8:
        suggestions.append(
            "Expected completion is low. Simplify the protocol or reduce participant burden if possible."
        )
    if config.usable_data_rate < 0.9:
        suggestions.append(
            "Usable-data loss is nontrivial. Pilot the data pipeline, instructions, and exclusion rules before the main collection."
        )
    if config.analysis_mode == "plan" and design_adjusted.total > 0 and initial_valid.total > 0:
        inflation = design_adjusted.total / max(initial_valid.total, 1)
        if inflation > 1.5:
            suggestions.append(
                "Design corrections increased the valid target substantially. Revisit clustering assumptions and consider operational alternatives."
            )
    if observed_analysis and observed_analysis.p_value > config.alpha:
        suggestions.append(
            "A non-significant achieved result does not prove the intervention has no effect. Report the observed effect and discuss precision, not only significance."
        )
    if observed_analysis and observed_analysis.achieved_power < 0.8:
        suggestions.append(
            "The achieved sample appears underpowered for the observed effect size. A larger replication may be more informative than a binary significant/non-significant interpretation."
        )
    return suggestions


def _build_sensitivity(config: StudyConfig) -> list[SensitivityRow]:
    rows: list[SensitivityRow] = []
    if config.analysis_mode != "plan":
        return rows
    variants: list[tuple[str, StudyConfig]] = []
    if config.outcome_type == "continuous":
        base = _planned_effect_size(config)
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
        nested = _calculate_no_sensitivity(variant)
        rows.append(
            SensitivityRow(
                label=label,
                control=nested.design_adjusted_valid.control,
                intervention=nested.design_adjusted_valid.intervention,
                total=nested.design_adjusted_valid.total,
                invited_total=nested.invited_needed.total,
            )
        )
    return rows


def _calculate_no_sensitivity(config: StudyConfig) -> SamplePlan:
    variant = config_from_dict(config_to_dict(config))
    variant.analysis_mode = "plan"
    alpha_adjusted = variant.alpha / variant.primary_comparisons
    z_alpha = _z_alpha(alpha_adjusted, variant.alternative)
    z_power = NORMAL.inv_cdf(variant.power)
    effect_size = _planned_effect_size(variant)
    initial_valid, method, formulas = _initial_valid_sample(variant, z_alpha, z_power, effect_size)
    fpc_adjusted, fpc_applied = _apply_fpc(initial_valid, variant)
    design_effect = _design_effect(variant)
    design_adjusted = _inflate_groups(fpc_adjusted, design_effect)
    assigned_needed, invited_needed, effective_data_rate = _correct_for_missing_data(design_adjusted, variant)
    achieved_power = _achieved_power(variant, design_adjusted, z_alpha, effect_size)
    return SamplePlan(
        config=variant,
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
        warnings=[],
        suggestions=[],
        sensitivity=[],
        observed_analysis=None,
    )


def _method_label(config: StudyConfig) -> str:
    if config.study_design == "parallel_two_group":
        return (
            "Normal approximation for two independent proportions"
            if config.outcome_type == "binary"
            else "Normal approximation for two independent means"
        )
    if config.study_design == "pretest_posttest_control":
        return "Approximate pre-test/post-test with control"
    return "Approximate one-group pre-test/post-test"


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _design_label(config: StudyConfig) -> str:
    mapping = {
        "parallel_two_group": "Two independent groups",
        "pretest_posttest_control": "Pre-test/post-test with control",
        "one_group_pre_post": "One-group pre-test/post-test",
    }
    return mapping[config.study_design]


def _group_text(config: StudyConfig, groups: GroupSizes) -> str:
    if config.study_design == "one_group_pre_post":
        return f"{groups.intervention} participants"
    return (
        f"{groups.control} {config.control_label} + "
        f"{groups.intervention} {config.intervention_label} = {groups.total}"
    )


def _render_en(plan: SamplePlan) -> str:
    c = plan.config
    lines = [
        f"Study: {c.study_name}",
        f"Research path: {_design_label(c)}",
        f"Run type: {'Plan required sample' if c.analysis_mode == 'plan' else 'Evaluate achieved result'}",
        f"Method: {plan.method}",
    ]
    if c.analysis_mode == "plan":
        lines.extend(
            [
                "",
                "Planning result",
                f"- Initial valid target: {_group_text(c, plan.initial_valid)}.",
                f"- Design-adjusted valid target: {_group_text(c, plan.design_adjusted_valid)}.",
                f"- To assign or start: {_group_text(c, plan.assigned_needed)}.",
                f"- To invite or contact: {_group_text(c, plan.invited_needed)}.",
                f"- Adjusted alpha: {plan.alpha_adjusted:.4f}; target power: {c.power:.1%}; achieved power at valid target: {plan.achieved_power_at_valid_target:.1%}.",
                f"- Effect value used: {plan.effect_size_used:.4f}; design effect: {plan.design_effect:.3f}; effective data rate: {plan.effective_data_rate:.1%}.",
            ]
        )
    if plan.observed_analysis:
        obs = plan.observed_analysis
        lines.extend(
            [
                "",
                "Achieved-result check",
                f"- Observed sample: {obs.observed_total} total participants.",
                f"- Observed effect entered: {obs.observed_effect_size:.4f}.",
                f"- Approximate z statistic: {obs.z_statistic:.4f}.",
                f"- Approximate p-value: {obs.p_value:.6f}.",
                f"- Approximate achieved power for the observed effect: {obs.achieved_power:.1%}.",
            ]
        )
    if plan.suggestions:
        lines.extend(["", "Suggestions"])
        lines.extend(f"- {item}" for item in plan.suggestions)
    if plan.warnings:
        lines.extend(["", "Warnings"])
        lines.extend(f"- {item}" for item in plan.warnings)
    if plan.formulas:
        lines.extend(["", "Formulas"])
        lines.extend(f"- {item}" for item in plan.formulas)
    return "\n".join(lines)


def _render_pt(plan: SamplePlan) -> str:
    c = plan.config
    path_map = {
        "parallel_two_group": "Dois grupos independentes",
        "pretest_posttest_control": "Pré-teste/pós-teste com controle",
        "one_group_pre_post": "Pré-teste/pós-teste com um grupo",
    }
    mode_map = {
        "plan": "Planejar amostra necessária",
        "evaluate": "Avaliar resultado alcançado",
    }
    lines = [
        f"Estudo: {c.study_name}",
        f"Caminho de pesquisa: {path_map[c.study_design]}",
        f"Tipo de execução: {mode_map[c.analysis_mode]}",
        f"Método: {plan.method}",
    ]
    if c.analysis_mode == "plan":
        lines.extend(
            [
                "",
                "Resultado do planejamento",
                f"- Alvo inicial válido: {_group_text(c, plan.initial_valid)}.",
                f"- Alvo válido após correções de desenho: {_group_text(c, plan.design_adjusted_valid)}.",
                f"- Participantes para iniciar/alocar: {_group_text(c, plan.assigned_needed)}.",
                f"- Pessoas para convidar/contatar: {_group_text(c, plan.invited_needed)}.",
                f"- Alfa ajustado: {plan.alpha_adjusted:.4f}; poder desejado: {c.power:.1%}; poder aproximado no alvo válido: {plan.achieved_power_at_valid_target:.1%}.",
                f"- Valor de efeito usado: {plan.effect_size_used:.4f}; efeito de desenho: {plan.design_effect:.3f}; taxa efetiva de dados: {plan.effective_data_rate:.1%}.",
            ]
        )
    if plan.observed_analysis:
        obs = plan.observed_analysis
        lines.extend(
            [
                "",
                "Verificação do resultado alcançado",
                f"- Amostra observada: {obs.observed_total} participantes ao todo.",
                f"- Efeito observado informado: {obs.observed_effect_size:.4f}.",
                f"- Estatística z aproximada: {obs.z_statistic:.4f}.",
                f"- Valor-p aproximado: {obs.p_value:.6f}.",
                f"- Poder aproximado alcançado para o efeito observado: {obs.achieved_power:.1%}.",
            ]
        )
    if plan.suggestions:
        lines.extend(["", "Sugestões"])
        lines.extend(f"- {item}" for item in plan.suggestions)
    if plan.warnings:
        lines.extend(["", "Avisos"])
        lines.extend(f"- {item}" for item in plan.warnings)
    if plan.formulas:
        lines.extend(["", "Fórmulas"])
        lines.extend(f"- {item}" for item in plan.formulas)
    return "\n".join(lines)
