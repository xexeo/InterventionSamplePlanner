"""Calculation API for intervention-study planning and result evaluation."""

# File version: 2.1; date: 2026-05-12

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import html
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
SUPPORTED_WORKFLOW_PATHS = {"plan_study", "evaluate_done", "evaluate_against_plan"}


@dataclass(slots=True)
class StudyConfig:
    """Inputs for planning or evaluating an intervention study."""

    study_name: str = "Untitled intervention study"
    language: str = "en"
    workflow_path: str = "plan_study"
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
    observed_control_events: int | None = None
    observed_intervention_events: int | None = None
    observed_pre_success_post_failure: int | None = None
    observed_pre_failure_post_success: int | None = None
    observed_effect_size: float | None = None

    had_planned_sample: bool = False
    planned_control_n: int | None = None
    planned_intervention_n: int | None = None
    planned_total_n: int | None = None
    planned_effect_size: float | None = None
    planned_alpha: float | None = None
    planned_power: float | None = None

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
class EvaluationTarget:
    label: str
    required_control: int
    required_intervention: int
    required_total: int
    additional_control: int
    additional_intervention: int
    additional_total: int
    achieved: bool


@dataclass(slots=True)
class ObservedAnalysis:
    observed_control: int
    observed_intervention: int
    observed_total: int
    observed_effect_size: float
    observed_control_rate: float | None
    observed_intervention_rate: float | None
    z_statistic: float
    p_value: float
    achieved_power: float
    method: str
    exact_p_value: float | None = None
    method_notes: list[str] = field(default_factory=list)
    benchmark_targets: list[EvaluationTarget] = field(default_factory=list)
    planned_targets: list[EvaluationTarget] = field(default_factory=list)


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
    if "workflow_path" not in cleaned:
        cleaned["workflow_path"] = _workflow_from_legacy_fields(cleaned)
    return StudyConfig(**cleaned)


def save_config(config: StudyConfig, path: str | Path) -> None:
    target = Path(path)
    payload = config_to_dict(config)
    payload.setdefault("_file_version", "2.1")
    payload.setdefault("_file_date", "2026-05-12")
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def load_config(path: str | Path) -> StudyConfig:
    source = Path(path)
    return config_from_dict(json.loads(source.read_text(encoding="utf-8")))


def calculate_plan(config: StudyConfig) -> SamplePlan:
    _normalize_workflow(config)
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


def render_report_html(plan: SamplePlan, language: str | None = None) -> str:
    title = html.escape(plan.config.study_name)
    body = html.escape(render_report(plan, language))
    return (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "  <meta charset=\"utf-8\">\n"
        f"  <title>{title}</title>\n"
        "  <style>\n"
        "    body { font-family: Segoe UI, Arial, sans-serif; margin: 2rem; line-height: 1.45; }\n"
        "    pre { white-space: pre-wrap; font-family: Consolas, monospace; background: #f7f7f7; padding: 1rem; }\n"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        f"<h1>{title}</h1>\n"
        f"<pre>{body}</pre>\n"
        "</body>\n"
        "</html>\n"
    )


def save_report_html(plan: SamplePlan, path: str | Path, language: str | None = None) -> None:
    Path(path).write_text(render_report_html(plan, language), encoding="utf-8")


def save_report_pdf(plan: SamplePlan, path: str | Path, language: str | None = None) -> None:
    lines = _wrap_report_lines(render_report(plan, language), width=92)
    pages = [lines[index : index + 48] for index in range(0, len(lines), 48)] or [[""]]
    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{3 + i * 2} 0 R" for i in range(len(pages)))
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode("ascii"))
    for index, page_lines in enumerate(pages):
        page_object_number = 3 + index * 2
        content_object_number = page_object_number + 1
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                f"/Resources << /Font << /F1 {3 + len(pages) * 2} 0 R >> >> "
                f"/Contents {content_object_number} 0 R >>"
            ).encode("ascii")
        )
        stream = _pdf_text_stream(page_lines)
        objects.append(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    _write_pdf(Path(path), objects)


def _wrap_report_lines(report: str, width: int) -> list[str]:
    wrapped: list[str] = []
    for line in report.splitlines():
        if not line:
            wrapped.append("")
            continue
        current = line
        while len(current) > width:
            breakpoint = current.rfind(" ", 0, width)
            if breakpoint <= 0:
                breakpoint = width
            wrapped.append(current[:breakpoint])
            current = current[breakpoint:].lstrip()
        wrapped.append(current)
    return wrapped


def _pdf_text_stream(lines: list[str]) -> bytes:
    commands = ["BT", "/F1 10 Tf", "50 750 Td", "14 TL"]
    for line in lines:
        commands.append(f"({_pdf_escape(line)}) Tj")
        commands.append("T*")
    commands.append("ET")
    return "\n".join(commands).encode("latin-1", errors="replace")


def _pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _write_pdf(path: Path, objects: list[bytes]) -> None:
    chunks = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
    offsets: list[int] = []
    position = len(chunks[0])
    for number, payload in enumerate(objects, start=1):
        offsets.append(position)
        chunk = f"{number} 0 obj\n".encode("ascii") + payload + b"\nendobj\n"
        chunks.append(chunk)
        position += len(chunk)
    xref_start = position
    xref = [f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("ascii")]
    xref.extend(f"{offset:010d} 00000 n \n".encode("ascii") for offset in offsets)
    trailer = (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_start}\n%%EOF\n"
    ).encode("ascii")
    path.write_bytes(b"".join(chunks + xref + [trailer]))


def _workflow_from_legacy_fields(data: dict[str, Any]) -> str:
    if data.get("analysis_mode") == "evaluate":
        return "evaluate_against_plan" if data.get("had_planned_sample") else "evaluate_done"
    return "plan_study"


def _normalize_workflow(config: StudyConfig) -> None:
    if config.workflow_path == "plan_study":
        config.analysis_mode = "plan"
        config.had_planned_sample = False
    elif config.workflow_path == "evaluate_done":
        config.analysis_mode = "evaluate"
        config.had_planned_sample = False
    elif config.workflow_path == "evaluate_against_plan":
        config.analysis_mode = "evaluate"
        config.had_planned_sample = True


def _validate_config(config: StudyConfig) -> None:
    if config.workflow_path not in SUPPORTED_WORKFLOW_PATHS:
        raise PlanningError(
            f"workflow_path must be one of: {', '.join(sorted(SUPPORTED_WORKFLOW_PATHS))}."
        )
    _normalize_workflow(config)
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

    if (
        config.outcome_type == "binary"
        and config.study_design != "parallel_two_group"
        and not (config.study_design == "one_group_pre_post" and config.analysis_mode == "evaluate")
    ):
        raise PlanningError(
            "Binary outcomes are supported for two independent groups and one-group paired evaluation."
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
        if config.outcome_type == "binary":
            if (
                config.observed_pre_success_post_failure is None
                or config.observed_pre_failure_post_success is None
            ):
                raise PlanningError(
                    "For one-group binary evaluation, provide the two discordant paired counts."
                )
            if config.observed_pre_success_post_failure < 0 or config.observed_pre_failure_post_success < 0:
                raise PlanningError("McNemar discordant counts must be zero or positive.")
            discordant = (
                config.observed_pre_success_post_failure
                + config.observed_pre_failure_post_success
            )
            if discordant <= 0:
                raise PlanningError("At least one discordant paired binary case is required.")
            if discordant > config.observed_total_n:
                raise PlanningError("Discordant paired counts cannot exceed observed_total_n.")
    else:
        if not config.observed_control_n or not config.observed_intervention_n:
            raise PlanningError(
                "observed_control_n and observed_intervention_n are required in achieved-result mode."
            )
        if config.observed_control_n <= 1 or config.observed_intervention_n <= 1:
            raise PlanningError("Observed group sizes must be at least 2.")
    if config.study_design == "parallel_two_group" and config.outcome_type == "binary":
        has_events = (
            config.observed_control_events is not None
            and config.observed_intervention_events is not None
        )
        if has_events:
            assert config.observed_control_n is not None
            assert config.observed_intervention_n is not None
            if not 0 <= config.observed_control_events <= config.observed_control_n:
                raise PlanningError("observed_control_events must be between 0 and observed_control_n.")
            if not 0 <= config.observed_intervention_events <= config.observed_intervention_n:
                raise PlanningError(
                    "observed_intervention_events must be between 0 and observed_intervention_n."
                )
            control_rate = config.observed_control_events / config.observed_control_n
            intervention_rate = config.observed_intervention_events / config.observed_intervention_n
            if control_rate == intervention_rate:
                raise PlanningError("Observed event rates are equal; no binary effect was observed.")
        elif config.observed_effect_size is None:
            raise PlanningError(
                "For binary achieved-result mode, provide observed event counts or an observed proportion difference."
            )
        elif not 0 < abs(config.observed_effect_size) < 1:
            raise PlanningError(
                "For binary achieved-result mode, observed_effect_size must be a proportion difference."
            )
    elif config.study_design == "one_group_pre_post" and config.outcome_type == "binary":
        pass
    elif config.observed_effect_size is None:
        raise PlanningError("observed_effect_size is required in achieved-result mode.")
    elif config.observed_effect_size == 0:
        raise PlanningError("observed_effect_size cannot be zero in achieved-result mode.")

    if config.had_planned_sample:
        has_planned_size = (
            bool(config.planned_total_n)
            if config.study_design == "one_group_pre_post"
            else bool(config.planned_total_n)
            or (bool(config.planned_control_n) and bool(config.planned_intervention_n))
        )
        if not has_planned_size:
            raise PlanningError(
                "When comparing with a previous plan, provide planned sample sizes or load a saved plan."
            )
        if config.planned_alpha is not None and not 0 < config.planned_alpha < 1:
            raise PlanningError("planned_alpha must be between 0 and 1.")
        if config.planned_power is not None and not 0 < config.planned_power < 1:
            raise PlanningError("planned_power must be between 0 and 1.")
        if config.planned_effect_size is not None and config.planned_effect_size <= 0:
            raise PlanningError("planned_effect_size must be positive.")
        if config.study_design == "one_group_pre_post":
            if config.planned_total_n is not None and config.planned_total_n <= 1:
                raise PlanningError("planned_total_n must be at least 2.")
        elif (
            config.planned_control_n is not None
            and config.planned_intervention_n is not None
            and (config.planned_control_n <= 1 or config.planned_intervention_n <= 1)
        ):
            raise PlanningError("planned group sizes must be at least 2.")


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
    if config.study_design == "one_group_pre_post":
        if config.outcome_type == "binary":
            n_total = int(config.observed_total_n or 0)
            improved = int(config.observed_pre_failure_post_success or 0)
            worsened = int(config.observed_pre_success_post_failure or 0)
            discordant = improved + worsened
            effect = abs(improved - worsened) / n_total
            z_stat = abs(improved - worsened) / math.sqrt(discordant)
            exact_p = _binomial_two_sided_p(min(improved, worsened), discordant, 0.5)
            achieved_power = _clamp(NORMAL.cdf(effect * math.sqrt(n_total) - z_alpha), 0.0, 1.0)
            groups = GroupSizes(0, n_total)
            return ObservedAnalysis(
                observed_control=0,
                observed_intervention=n_total,
                observed_total=n_total,
                observed_effect_size=effect,
                observed_control_rate=worsened / n_total,
                observed_intervention_rate=improved / n_total,
                z_statistic=z_stat,
                p_value=exact_p,
                achieved_power=achieved_power,
                method="Exact McNemar paired-binary evaluation",
                exact_p_value=exact_p,
                method_notes=[
                    "McNemar uses only discordant paired cases: pre success/post failure and pre failure/post success.",
                    "The p-value is exact binomial; achieved power and benchmark gaps remain approximate."
                ],
                benchmark_targets=_evaluation_targets(config, max(effect, 1e-9), groups, z_alpha),
                planned_targets=_planned_targets(config, groups),
            )
        effect = abs(config.observed_effect_size or 0.0)
        n_total = int(config.observed_total_n or 0)
        groups = GroupSizes(0, n_total)
        z_stat = effect * math.sqrt(n_total)
        achieved_power = _clamp(NORMAL.cdf(z_stat - z_alpha), 0.0, 1.0)
        return ObservedAnalysis(
            observed_control=0,
            observed_intervention=n_total,
            observed_total=n_total,
            observed_effect_size=effect,
            observed_control_rate=None,
            observed_intervention_rate=None,
            z_statistic=z_stat,
            p_value=_p_value(z_stat, config.alternative),
            achieved_power=achieved_power,
            method="Approximate paired standardized-mean-change evaluation",
            method_notes=[
                "For continuous one-group pre/post studies, the app treats the observed effect as a standardized mean change."
            ],
            benchmark_targets=_evaluation_targets(config, effect, groups, z_alpha),
            planned_targets=_planned_targets(config, groups),
        )
    control = int(config.observed_control_n or 0)
    intervention = int(config.observed_intervention_n or 0)
    groups = GroupSizes(control, intervention)
    total = control + intervention
    k = intervention / control
    control_rate: float | None = None
    intervention_rate: float | None = None
    if config.study_design == "pretest_posttest_control":
        effect = abs(config.observed_effect_size or 0.0)
        base = math.sqrt(control / (1 + 1 / k))
        efficiency_gain = 1 / math.sqrt(max(0.05, 1 - config.pre_post_correlation**2))
        z_stat = effect * base * efficiency_gain
        achieved_power = _clamp(NORMAL.cdf(z_stat - z_alpha), 0.0, 1.0)
        method = "Approximate ANCOVA-style pre-test/post-test with control evaluation"
        method_notes = [
            "The pre/post control path uses an ANCOVA-style precision gain from the pre/post correlation.",
            "Fit the final study with the actual post-test outcome and baseline covariate when possible.",
        ]
    elif config.outcome_type == "continuous":
        effect = abs(config.observed_effect_size or 0.0)
        z_stat = effect * math.sqrt(control / (1 + 1 / k))
        achieved_power = _clamp(NORMAL.cdf(z_stat - z_alpha), 0.0, 1.0)
        method = "Approximate two-group continuous evaluation"
        method_notes = []
    else:
        exact_p: float | None = None
        if config.observed_control_events is not None and config.observed_intervention_events is not None:
            p0 = config.observed_control_events / control
            p1 = config.observed_intervention_events / intervention
            control_rate = p0
            intervention_rate = p1
            effect = abs(p1 - p0)
            exact_p = _fisher_exact_p(
                config.observed_control_events,
                control - config.observed_control_events,
                config.observed_intervention_events,
                intervention - config.observed_intervention_events,
                config.alternative,
            )
        else:
            effect = abs(config.observed_effect_size or 0.0)
            p0 = config.proportion_control
            p1 = _clamp(p0 + effect, 0.001, 0.999)
            control_rate = p0
            intervention_rate = p1
        p_bar = (p0 + p1) / 2
        pooled = max((1 + 1 / k) * p_bar * (1 - p_bar), 1e-12)
        unpooled = max(p0 * (1 - p0) + p1 * (1 - p1) / k, 1e-12)
        z_stat = math.sqrt(control) * effect / math.sqrt(pooled)
        z_beta = (math.sqrt(control) * effect - z_alpha * math.sqrt(pooled)) / math.sqrt(unpooled)
        achieved_power = _clamp(NORMAL.cdf(z_beta), 0.0, 1.0)
        small_sample = total < 80
        if exact_p is not None:
            cells = [
                int(config.observed_control_events or 0),
                control - int(config.observed_control_events or 0),
                int(config.observed_intervention_events or 0),
                intervention - int(config.observed_intervention_events or 0),
            ]
            small_sample = min(cells) < 5 or total < 80
        if exact_p is not None and small_sample:
            p_value = exact_p
            method = "Fisher exact two-group binary evaluation"
        else:
            p_value = _p_value(z_stat, config.alternative)
            method = "Approximate two-group proportion-difference evaluation"
        method_notes = [
            "Fisher's exact p-value is calculated when event counts are available.",
            "For small samples or sparse cells, the exact p-value is used as the reported p-value.",
        ]
        return ObservedAnalysis(
            observed_control=control,
            observed_intervention=intervention,
            observed_total=total,
            observed_effect_size=effect,
            observed_control_rate=control_rate,
            observed_intervention_rate=intervention_rate,
            z_statistic=z_stat,
            p_value=p_value,
            achieved_power=achieved_power,
            method=method,
            exact_p_value=exact_p,
            method_notes=method_notes,
            benchmark_targets=_evaluation_targets(
                config,
                effect,
                groups,
                z_alpha,
                control_rate=control_rate,
                intervention_rate=intervention_rate,
            ),
            planned_targets=_planned_targets(config, groups),
        )
    return ObservedAnalysis(
        observed_control=control,
        observed_intervention=intervention,
        observed_total=total,
        observed_effect_size=effect,
        observed_control_rate=control_rate,
        observed_intervention_rate=intervention_rate,
        z_statistic=z_stat,
        p_value=_p_value(z_stat, config.alternative),
        achieved_power=achieved_power,
        method=method,
        method_notes=method_notes,
        benchmark_targets=_evaluation_targets(
            config,
            effect,
            groups,
            z_alpha,
            control_rate=control_rate,
            intervention_rate=intervention_rate,
        ),
        planned_targets=_planned_targets(config, groups),
    )


def _evaluation_targets(
    config: StudyConfig,
    effect_size: float,
    observed_groups: GroupSizes,
    z_alpha: float,
    control_rate: float | None = None,
    intervention_rate: float | None = None,
) -> list[EvaluationTarget]:
    targets: list[EvaluationTarget] = []
    for alpha in (0.05, 0.10):
        adjusted = alpha / config.primary_comparisons
        required = _required_groups_for_z(
            config,
            effect_size,
            observed_groups,
            _z_alpha(adjusted, config.alternative),
            control_rate,
            intervention_rate,
        )
        required = _cluster_adjusted_target(required, config)
        targets.append(_target_gap(f"p < {alpha:.2f}", required, observed_groups))
    for desired_power in (0.80, 0.90):
        required = _required_groups_for_power(
            config,
            effect_size,
            observed_groups,
            z_alpha,
            desired_power,
            control_rate,
            intervention_rate,
        )
        required = _cluster_adjusted_target(required, config)
        targets.append(_target_gap(f"power >= {desired_power:.0%}", required, observed_groups))
    return targets


def _cluster_adjusted_target(groups: GroupSizes, config: StudyConfig) -> GroupSizes:
    design_effect = _design_effect(config)
    if design_effect <= 1:
        return groups
    return _inflate_groups(groups, design_effect)


def _required_groups_for_z(
    config: StudyConfig,
    effect_size: float,
    observed_groups: GroupSizes,
    z_required: float,
    control_rate: float | None,
    intervention_rate: float | None,
) -> GroupSizes:
    if config.study_design == "one_group_pre_post":
        total = math.ceil((z_required / effect_size) ** 2)
        return GroupSizes(0, max(2, total))
    k = _observed_ratio(config, observed_groups)
    if config.study_design == "pretest_posttest_control":
        efficiency_gain = 1 / math.sqrt(max(0.05, 1 - config.pre_post_correlation**2))
        control = math.ceil(((z_required / (effect_size * efficiency_gain)) ** 2) * (1 + 1 / k))
    elif config.outcome_type == "continuous":
        control = math.ceil((z_required / effect_size) ** 2 * (1 + 1 / k))
    else:
        p0 = control_rate if control_rate is not None else config.proportion_control
        p1 = intervention_rate if intervention_rate is not None else _clamp(p0 + effect_size, 0.001, 0.999)
        p_bar = (p0 + p1) / 2
        pooled = max((1 + 1 / k) * p_bar * (1 - p_bar), 1e-12)
        control = math.ceil((z_required * math.sqrt(pooled) / effect_size) ** 2)
    return GroupSizes(max(2, control), max(2, math.ceil(control * k)))


def _required_groups_for_power(
    config: StudyConfig,
    effect_size: float,
    observed_groups: GroupSizes,
    z_alpha: float,
    desired_power: float,
    control_rate: float | None,
    intervention_rate: float | None,
) -> GroupSizes:
    z_power = NORMAL.inv_cdf(desired_power)
    if config.study_design == "one_group_pre_post":
        total = math.ceil(((z_alpha + z_power) / effect_size) ** 2)
        return GroupSizes(0, max(2, total))
    k = _observed_ratio(config, observed_groups)
    if config.study_design == "pretest_posttest_control":
        adjusted_effect = effect_size / math.sqrt(max(0.05, 1 - config.pre_post_correlation**2))
        control = math.ceil(((z_alpha + z_power) / adjusted_effect) ** 2 * (1 + 1 / k))
    elif config.outcome_type == "continuous":
        control = math.ceil(((z_alpha + z_power) / effect_size) ** 2 * (1 + 1 / k))
    else:
        p0 = control_rate if control_rate is not None else config.proportion_control
        p1 = intervention_rate if intervention_rate is not None else _clamp(p0 + effect_size, 0.001, 0.999)
        p_bar = (p0 + p1) / 2
        pooled = max((1 + 1 / k) * p_bar * (1 - p_bar), 1e-12)
        unpooled = max(p0 * (1 - p0) + p1 * (1 - p1) / k, 1e-12)
        numerator = z_alpha * math.sqrt(pooled) + z_power * math.sqrt(unpooled)
        control = math.ceil((numerator / effect_size) ** 2)
    return GroupSizes(max(2, control), max(2, math.ceil(control * k)))


def _planned_targets(config: StudyConfig, observed_groups: GroupSizes) -> list[EvaluationTarget]:
    if not config.had_planned_sample:
        return []
    if config.study_design == "one_group_pre_post":
        if not config.planned_total_n:
            return []
        required = GroupSizes(0, config.planned_total_n)
    elif config.planned_control_n and config.planned_intervention_n:
        required = GroupSizes(config.planned_control_n, config.planned_intervention_n)
    elif config.planned_total_n:
        k = _observed_ratio(config, observed_groups)
        control = max(2, math.ceil(config.planned_total_n / (1 + k)))
        required = GroupSizes(control, max(2, config.planned_total_n - control))
    else:
        return []
    return [_target_gap("planned sample", required, observed_groups)]


def _target_gap(label: str, required: GroupSizes, observed: GroupSizes) -> EvaluationTarget:
    additional_control = max(0, required.control - observed.control)
    additional_intervention = max(0, required.intervention - observed.intervention)
    return EvaluationTarget(
        label=label,
        required_control=required.control,
        required_intervention=required.intervention,
        required_total=required.total,
        additional_control=additional_control,
        additional_intervention=additional_intervention,
        additional_total=additional_control + additional_intervention,
        achieved=additional_control == 0 and additional_intervention == 0,
    )


def _observed_ratio(config: StudyConfig, observed_groups: GroupSizes) -> float:
    if observed_groups.control > 0 and observed_groups.intervention > 0:
        return observed_groups.intervention / observed_groups.control
    return max(config.allocation_ratio, 1e-9)


def _p_value(z_stat: float, alternative: str) -> float:
    if alternative == "two_sided":
        return 2 * (1 - NORMAL.cdf(abs(z_stat)))
    return 1 - NORMAL.cdf(abs(z_stat))


def _binomial_two_sided_p(successes: int, trials: int, probability: float) -> float:
    observed = _binomial_pmf(successes, trials, probability)
    total = 0.0
    for value in range(trials + 1):
        current = _binomial_pmf(value, trials, probability)
        if current <= observed + 1e-15:
            total += current
    return _clamp(total, 0.0, 1.0)


def _binomial_pmf(successes: int, trials: int, probability: float) -> float:
    return math.comb(trials, successes) * probability**successes * (1 - probability) ** (trials - successes)


def _fisher_exact_p(
    control_events: int,
    control_non_events: int,
    intervention_events: int,
    intervention_non_events: int,
    alternative: str,
) -> float:
    total_events = control_events + intervention_events
    intervention_total = intervention_events + intervention_non_events
    grand_total = control_events + control_non_events + intervention_events + intervention_non_events
    lower = max(0, intervention_total - (grand_total - total_events))
    upper = min(intervention_total, total_events)
    observed = intervention_events
    observed_probability = _hypergeom_pmf(observed, total_events, grand_total - total_events, intervention_total)
    probability = 0.0
    for value in range(lower, upper + 1):
        current = _hypergeom_pmf(value, total_events, grand_total - total_events, intervention_total)
        if alternative == "greater" and value >= observed:
            probability += current
        elif alternative == "less" and value <= observed:
            probability += current
        elif alternative == "two_sided" and current <= observed_probability + 1e-15:
            probability += current
    return _clamp(probability, 0.0, 1.0)


def _hypergeom_pmf(successes: int, successes_population: int, failures_population: int, draws: int) -> float:
    return (
        math.comb(successes_population, successes)
        * math.comb(failures_population, draws - successes)
        / math.comb(successes_population + failures_population, draws)
    )


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
        suggestions.append(
            "For the final analysis, prefer an ANCOVA-style model that predicts post-test from group assignment while adjusting for baseline pre-test."
        )
    else:
        suggestions.append(
            "Without a control group, interpret improvement cautiously: learning gains may reflect practice, maturation, or ordinary instruction."
        )
        suggestions.append(
            "If possible, add a control group in a later study or replicate the result in a second cohort."
        )
        if config.outcome_type == "binary" and config.analysis_mode == "evaluate":
            suggestions.append(
                "For paired before/after binary outcomes, the app uses McNemar's exact test from the two discordant cells; unchanged pairs describe the sample but do not drive the test."
            )
    if config.cluster_average_size > 1 and config.intraclass_correlation > 0:
        suggestions.append(
            "Because participants are clustered, adding more clusters may help more than adding more people inside the same cluster."
        )
        suggestions.append(
            "For a full cluster-randomized study, also plan the number of clusters per arm and keep analysis aligned with the randomization unit."
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
    if observed_analysis:
        if observed_analysis.p_value <= 0.05:
            suggestions.append(
                "The achieved p-value is below the conventional 0.05 benchmark. Interpret it together with the observed effect size, design limits, and data quality."
            )
        elif observed_analysis.p_value <= 0.10:
            suggestions.append(
                "The achieved p-value is below 0.10 but not 0.05. This is usually exploratory evidence, not a strong confirmatory result."
            )
        else:
            suggestions.append(
                "A non-significant achieved result does not prove the intervention has no effect. Report the observed effect and discuss precision, not only significance."
            )
        if observed_analysis.achieved_power >= 0.8:
            suggestions.append(
                "The achieved sample reaches the common 80% power benchmark for the observed effect size."
            )
        else:
            suggestions.append(
                "The achieved sample appears underpowered for the observed effect size. A larger replication may be more informative than a binary significant/non-significant interpretation."
            )
        if observed_analysis.exact_p_value is not None:
            suggestions.append(
                "An exact p-value is available for this result. Use it preferentially when samples are small or binary outcome cells are sparse."
            )
        if any(item.additional_total > 0 for item in observed_analysis.benchmark_targets):
            suggestions.append(
                "The plan/benchmark table separates what was achieved from how many additional valid observations would be needed for common thresholds."
            )
        for target in observed_analysis.benchmark_targets:
            if target.achieved:
                suggestions.append(f"Benchmark reached for {target.label}.")
            else:
                suggestions.append(
                    f"To reach {target.label} with the observed effect and allocation, add about "
                    f"{target.additional_total} valid participants."
                )
        for target in observed_analysis.planned_targets:
            if target.achieved:
                suggestions.append("The observed valid sample reached the sample size from the loaded or entered plan.")
            else:
                suggestions.append(
                    "The observed valid sample is below the loaded or entered plan by about "
                    f"{target.additional_total} valid participants."
                )
        if config.had_planned_sample and config.planned_effect_size:
            if observed_analysis.observed_effect_size < config.planned_effect_size:
                suggestions.append(
                    "The observed effect is smaller than the planned effect. Even a study with the planned sample can miss conventional thresholds when the real effect is smaller than expected."
                )
            else:
                suggestions.append(
                    "The observed effect is at least as large as the planned effect. If thresholds were not reached, sample size, allocation, or attrition are likely limiting factors."
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


def _target_text_en(config: StudyConfig, target: EvaluationTarget) -> str:
    status = "reached" if target.achieved else f"needs {target.additional_total} more valid participants"
    if config.study_design == "one_group_pre_post":
        return f"- {target.label}: requires {target.required_total} valid participants; {status}."
    return (
        f"- {target.label}: requires {target.required_control} {config.control_label} and "
        f"{target.required_intervention} {config.intervention_label}; {status}."
    )


def _target_text_pt(config: StudyConfig, target: EvaluationTarget) -> str:
    status = "alcancado" if target.achieved else f"faltam {target.additional_total} participantes validos"
    if config.study_design == "one_group_pre_post":
        return f"- {target.label}: exige {target.required_total} participantes validos; {status}."
    return (
        f"- {target.label}: exige {target.required_control} {config.control_label} e "
        f"{target.required_intervention} {config.intervention_label}; {status}."
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
        if obs.exact_p_value is not None:
            lines.append(f"- Exact p-value: {obs.exact_p_value:.6f}.")
        if obs.method_notes:
            lines.extend(f"- Method note: {item}" for item in obs.method_notes)
        if obs.observed_control_rate is not None and obs.observed_intervention_rate is not None:
            lines.extend(
                [
                    f"- Observed control rate: {obs.observed_control_rate:.1%}.",
                    f"- Observed intervention rate: {obs.observed_intervention_rate:.1%}.",
                ]
            )
        if obs.planned_targets:
            lines.extend(["", "Comparison with previous plan"])
            lines.extend(_target_text_en(c, target) for target in obs.planned_targets)
            if c.planned_effect_size:
                lines.append(f"- Planned effect: {c.planned_effect_size:.4f}.")
            if c.planned_alpha:
                lines.append(f"- Planned alpha: {c.planned_alpha:.4f}.")
            if c.planned_power:
                lines.append(f"- Planned power: {c.planned_power:.1%}.")
        if obs.benchmark_targets:
            lines.extend(["", "Conventional benchmark gaps"])
            lines.extend(_target_text_en(c, target) for target in obs.benchmark_targets)
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
        if obs.exact_p_value is not None:
            lines.append(f"- Valor-p exato: {obs.exact_p_value:.6f}.")
        if obs.method_notes:
            lines.extend(f"- Nota de metodo: {item}" for item in obs.method_notes)
        if obs.observed_control_rate is not None and obs.observed_intervention_rate is not None:
            lines.extend(
                [
                    f"- Taxa observada no controle: {obs.observed_control_rate:.1%}.",
                    f"- Taxa observada na intervencao: {obs.observed_intervention_rate:.1%}.",
                ]
            )
        if obs.planned_targets:
            lines.extend(["", "Comparacao com o plano anterior"])
            lines.extend(_target_text_pt(c, target) for target in obs.planned_targets)
            if c.planned_effect_size:
                lines.append(f"- Efeito planejado: {c.planned_effect_size:.4f}.")
            if c.planned_alpha:
                lines.append(f"- Alfa planejado: {c.planned_alpha:.4f}.")
            if c.planned_power:
                lines.append(f"- Poder planejado: {c.planned_power:.1%}.")
        if obs.benchmark_targets:
            lines.extend(["", "Lacunas para benchmarks convencionais"])
            lines.extend(_target_text_pt(c, target) for target in obs.benchmark_targets)
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
