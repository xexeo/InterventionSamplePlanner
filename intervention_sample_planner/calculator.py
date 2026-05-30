"""Calculation API for intervention-study planning and result evaluation."""

# File version: 2.4; date: 2026-05-30

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import html
import json
import math
from pathlib import Path
import re
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
    "one_group_post_survey",
    "stratified_post_survey",
}
SUPPORTED_ANALYSIS_MODES = {"plan", "evaluate"}
SUPPORTED_WORKFLOW_PATHS = {"plan_study", "evaluate_done", "evaluate_against_plan"}
SUPPORTED_SURVEY_GOALS = {"favorable_proportion", "mean_score"}
SUPPORTED_STRATIFIED_ALLOCATIONS = {"proportional", "equal", "minimum_per_stratum", "manual"}


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

    survey_analysis_goal: str = "favorable_proportion"
    survey_scale_min: float = 1.0
    survey_scale_max: float = 5.0
    survey_scale_points: int = 5
    survey_favorable_threshold: float = 4.0
    survey_target_proportion: float = 0.70
    survey_expected_proportion: float = 0.50
    survey_margin_of_error: float = 0.05
    survey_expected_sd: float | None = None
    survey_mean_margin_of_error: float = 0.20
    survey_target_mean: float | None = None

    strata_definition: str = ""
    stratified_allocation_method: str = "proportional"
    stratified_min_per_stratum: int = 30
    stratified_target_total: int | None = None
    stratified_population_known: bool = True
    stratified_use_weights: bool = True

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
    observed_survey_counts: str = ""
    observed_survey_favorable_count: int | None = None
    observed_survey_mean: float | None = None
    observed_survey_sd: float | None = None
    observed_strata_counts: str = ""

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
class CapacityRow:
    label: str
    alpha: float
    power: float
    effect_size: float | None
    effect_label: str
    control: int
    intervention: int
    total: int
    note: str


@dataclass(slots=True)
class SurveyCategoryRow:
    label: str
    count: int
    proportion: float
    ci_low: float
    ci_high: float
    favorable: bool
    missing: bool = False


@dataclass(slots=True)
class SurveyAnalysis:
    confidence_level: float
    valid_n: int
    missing_n: int
    favorable_count: int | None
    favorable_proportion: float | None
    favorable_ci_low: float | None
    favorable_ci_high: float | None
    target_proportion: float | None
    target_reached: bool | None
    margin_of_error: float | None
    mean: float | None
    sd: float | None
    mean_ci_low: float | None
    mean_ci_high: float | None
    target_mean: float | None
    target_mean_reached: bool | None
    category_rows: list[SurveyCategoryRow] = field(default_factory=list)


@dataclass(slots=True)
class StratumDefinition:
    stratum_id: str
    label: str
    population_n: int | None
    population_proportion: float | None
    target_valid_n: int | None


@dataclass(slots=True)
class StratumPlanRow:
    stratum_id: str
    label: str
    population_n: int | None
    population_proportion: float
    target_valid_n: int
    assigned_needed: int
    invited_needed: int
    response_rate: float
    completion_rate: float
    usable_data_rate: float
    weight: float | None
    note: str


@dataclass(slots=True)
class StratumObservedRow:
    stratum_id: str
    label: str
    expected_proportion: float
    observed_valid_n: int
    observed_missing_n: int
    observed_share: float | None
    representation_ratio: float | None
    weight: float | None
    favorable_count: int | None
    favorable_proportion: float | None
    favorable_ci_low: float | None
    favorable_ci_high: float | None
    mean: float | None
    status: str
    note: str


@dataclass(slots=True)
class StratifiedSurveyAnalysis:
    allocation_method: str
    confidence_level: float
    target_total_valid: int
    assigned_total: int
    invited_total: int
    effective_data_rate: float
    use_weights: bool
    plan_rows: list[StratumPlanRow] = field(default_factory=list)
    observed_rows: list[StratumObservedRow] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ObservedAnalysis:
    observed_control: int
    observed_intervention: int
    observed_total: int
    observed_effect_size: float | None
    observed_control_rate: float | None
    observed_intervention_rate: float | None
    z_statistic: float | None
    p_value: float | None
    achieved_power: float | None
    method: str
    exact_p_value: float | None = None
    method_notes: list[str] = field(default_factory=list)
    benchmark_targets: list[EvaluationTarget] = field(default_factory=list)
    planned_targets: list[EvaluationTarget] = field(default_factory=list)
    capacity_rows: list[CapacityRow] = field(default_factory=list)
    survey_analysis: SurveyAnalysis | None = None


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
    stratified_survey_analysis: StratifiedSurveyAnalysis | None = None


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
    payload.setdefault("_file_version", "2.4")
    payload.setdefault("_file_date", "2026-05-30")
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
    stratified_analysis = _stratified_survey_analysis(config, z_alpha, design_adjusted, observed_analysis)
    if stratified_analysis:
        warnings.extend(stratified_analysis.warnings)
        if config.analysis_mode == "plan" and stratified_analysis.plan_rows:
            assigned_needed = GroupSizes(0, stratified_analysis.assigned_total)
            invited_needed = GroupSizes(0, stratified_analysis.invited_total)
    suggestions = _build_suggestions(config, initial_valid, design_adjusted, observed_analysis)
    if stratified_analysis:
        suggestions.extend(_stratified_survey_suggestions(config, stratified_analysis))
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
        stratified_survey_analysis=stratified_analysis,
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
    if config.survey_analysis_goal not in SUPPORTED_SURVEY_GOALS:
        raise PlanningError("survey_analysis_goal must be 'favorable_proportion' or 'mean_score'.")
    if config.stratified_allocation_method not in SUPPORTED_STRATIFIED_ALLOCATIONS:
        raise PlanningError(
            "stratified_allocation_method must be one of: proportional, equal, minimum_per_stratum, manual."
        )
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
    _validate_survey_settings(config)
    if config.study_design == "stratified_post_survey":
        _validate_stratified_settings(config)

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
    if config.study_design in {"one_group_post_survey", "stratified_post_survey"}:
        if config.study_design == "stratified_post_survey":
            _parse_strata_definition(config.strata_definition)
            _parse_observed_strata_counts(config.observed_strata_counts)
        parsed = _parse_survey_counts(config.observed_survey_counts)
        has_counts = bool(parsed) or bool(config.observed_strata_counts.strip())
        has_total = config.observed_total_n is not None
        strata_total = _stratified_observed_total(config) if config.study_design == "stratified_post_survey" else 0
        if not has_counts and not strata_total and (not has_total or config.observed_total_n is None or config.observed_total_n < 2):
            raise PlanningError(
                "Post-intervention survey evaluation needs observed_total_n or observed_survey_counts."
            )
        if has_total and config.observed_total_n is not None and config.observed_total_n < 2:
            raise PlanningError("observed_total_n must be at least 2 for survey evaluation.")
        valid_n = _survey_valid_n_from_counts(parsed)
        total_n = int(config.observed_total_n or strata_total or _survey_total_n_from_counts(parsed))
        if config.observed_survey_favorable_count is not None:
            if config.observed_survey_favorable_count < 0 or config.observed_survey_favorable_count > total_n:
                raise PlanningError("observed_survey_favorable_count must be between 0 and observed_total_n.")
        if config.survey_analysis_goal == "favorable_proportion" and not has_counts and config.observed_survey_favorable_count is None:
            pass
        if config.survey_analysis_goal == "mean_score" and not has_counts:
            if config.observed_survey_mean is None or config.observed_survey_sd is None:
                raise PlanningError(
                    "Mean-score survey evaluation needs observed_survey_counts or observed_survey_mean plus observed_survey_sd."
                )
            if not config.survey_scale_min <= config.observed_survey_mean <= config.survey_scale_max:
                raise PlanningError("observed_survey_mean must be inside the survey scale.")
            if config.observed_survey_sd <= 0:
                raise PlanningError("observed_survey_sd must be positive.")
        if bool(parsed) and valid_n <= 0:
            raise PlanningError("observed_survey_counts must include at least one numeric response category.")
    elif config.study_design == "one_group_pre_post":
        if not config.observed_total_n or config.observed_total_n <= 1:
            raise PlanningError("observed_total_n must be at least 2 in achieved-result mode.")
        if config.outcome_type == "binary":
            has_worsened = config.observed_pre_success_post_failure is not None
            has_improved = config.observed_pre_failure_post_success is not None
            if has_worsened != has_improved:
                raise PlanningError(
                    "For one-group binary evaluation, provide both discordant paired counts, or leave both empty for a sample-size capacity table."
                )
            if not has_worsened and not has_improved:
                pass
            else:
                assert config.observed_pre_success_post_failure is not None
                assert config.observed_pre_failure_post_success is not None
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
        has_control = config.observed_control_n is not None
        has_intervention = config.observed_intervention_n is not None
        has_group_sizes = has_control and has_intervention
        has_total = config.observed_total_n is not None
        if has_control != has_intervention:
            raise PlanningError(
                "Provide both observed_control_n and observed_intervention_n, or leave both empty and provide observed_total_n for allocation scenarios."
            )
        if not has_group_sizes and not has_total:
            raise PlanningError(
                "Provide observed group sizes or observed_total_n in achieved-result mode."
            )
        if has_group_sizes and (config.observed_control_n <= 1 or config.observed_intervention_n <= 1):
            raise PlanningError("Observed group sizes must be at least 2.")
        if not has_group_sizes and (config.observed_total_n is None or config.observed_total_n <= 3):
            raise PlanningError("observed_total_n must be at least 4 for two-group allocation scenarios.")
    if config.study_design == "parallel_two_group" and config.outcome_type == "binary":
        has_events = (
            config.observed_control_events is not None
            and config.observed_intervention_events is not None
        )
        has_one_event_count = (
            config.observed_control_events is not None
            or config.observed_intervention_events is not None
        )
        if has_events:
            if config.observed_control_n is None or config.observed_intervention_n is None:
                raise PlanningError("Binary event counts require observed_control_n and observed_intervention_n.")
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
        elif has_one_event_count:
            raise PlanningError(
                "For binary achieved-result mode, provide both event counts, or leave both empty for a sample-size capacity table."
            )
        elif config.observed_effect_size is None:
            pass
        elif not 0 < abs(config.observed_effect_size) < 1:
            raise PlanningError(
                "For binary achieved-result mode, observed_effect_size must be a proportion difference."
            )
    elif config.study_design == "one_group_pre_post" and config.outcome_type == "binary":
        pass
    elif config.observed_effect_size is None:
        pass
    elif config.observed_effect_size == 0:
        raise PlanningError("observed_effect_size cannot be zero in achieved-result mode.")

    if config.had_planned_sample:
        has_planned_size = (
            bool(config.planned_total_n)
            if config.study_design in {"one_group_pre_post", "one_group_post_survey", "stratified_post_survey"}
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
        if config.study_design in {"one_group_pre_post", "one_group_post_survey", "stratified_post_survey"}:
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


def _validate_survey_settings(config: StudyConfig) -> None:
    if config.survey_scale_max <= config.survey_scale_min:
        raise PlanningError("survey_scale_max must be greater than survey_scale_min.")
    if config.survey_scale_points < 2:
        raise PlanningError("survey_scale_points must be at least 2.")
    if not config.survey_scale_min <= config.survey_favorable_threshold <= config.survey_scale_max:
        raise PlanningError("survey_favorable_threshold must be inside the survey scale.")
    if not 0 < config.survey_target_proportion < 1:
        raise PlanningError("survey_target_proportion must be between 0 and 1.")
    if not 0 < config.survey_expected_proportion < 1:
        raise PlanningError("survey_expected_proportion must be between 0 and 1.")
    if not 0 < config.survey_margin_of_error < 1:
        raise PlanningError("survey_margin_of_error must be between 0 and 1.")
    if config.survey_expected_sd is not None and config.survey_expected_sd <= 0:
        raise PlanningError("survey_expected_sd must be positive when provided.")
    if config.survey_mean_margin_of_error <= 0:
        raise PlanningError("survey_mean_margin_of_error must be positive.")
    if config.survey_target_mean is not None and not (
        config.survey_scale_min <= config.survey_target_mean <= config.survey_scale_max
    ):
        raise PlanningError("survey_target_mean must be inside the survey scale.")


def _validate_stratified_settings(config: StudyConfig) -> None:
    strata = _parse_strata_definition(config.strata_definition)
    if len(strata) < 2:
        raise PlanningError("strata_definition must describe at least two strata for stratified surveys.")
    if config.stratified_min_per_stratum < 1:
        raise PlanningError("stratified_min_per_stratum must be at least 1.")
    if config.stratified_target_total is not None and config.stratified_target_total < len(strata):
        raise PlanningError("stratified_target_total must be at least the number of strata.")
    if config.stratified_allocation_method == "manual" and any(item.target_valid_n is None for item in strata):
        raise PlanningError("Manual stratified allocation requires target_valid_n for every stratum.")


def _planned_effect_size(config: StudyConfig) -> float:
    if config.study_design in {"one_group_post_survey", "stratified_post_survey"}:
        if config.survey_analysis_goal == "mean_score":
            return config.survey_mean_margin_of_error
        return config.survey_margin_of_error
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
    if config.study_design == "stratified_post_survey":
        return _stratified_post_survey_initial(config, z_alpha)
    if config.study_design == "one_group_post_survey":
        return _one_group_post_survey_initial(config, z_alpha)
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


def _one_group_post_survey_initial(
    config: StudyConfig, z_alpha: float
) -> tuple[GroupSizes, str, list[str]]:
    if config.survey_analysis_goal == "mean_score":
        sd = _survey_planning_sd(config)
        margin = config.survey_mean_margin_of_error
        n_total = (z_alpha * sd / margin) ** 2
        formulas = [
            "confidence = 1 - alpha; power is not used for descriptive survey precision",
            "n = (z_confidence * expected_sd / margin_of_error)^2",
            "If expected_sd is blank, the app uses one quarter of the scale range as a rough planning value.",
        ]
        return (
            GroupSizes(0, math.ceil(n_total)),
            "One-group post-intervention survey mean confidence interval",
            formulas,
        )
    p = _clamp(config.survey_expected_proportion, 0.001, 0.999)
    margin = config.survey_margin_of_error
    n_total = z_alpha**2 * p * (1 - p) / margin**2
    formulas = [
        "confidence = 1 - alpha; power is not used for descriptive survey precision",
        "n = z_confidence^2 * expected_proportion * (1 - expected_proportion) / margin_of_error^2",
        "Use expected_proportion = 0.50 when no prior evidence exists; it gives the largest conservative sample.",
    ]
    return (
        GroupSizes(0, math.ceil(n_total)),
        "One-group post-intervention survey favorable-proportion confidence interval",
        formulas,
    )


def _stratified_post_survey_initial(
    config: StudyConfig, z_alpha: float
) -> tuple[GroupSizes, str, list[str]]:
    base_groups, _method, formulas = _one_group_post_survey_initial(config, z_alpha)
    target_total = int(config.stratified_target_total or base_groups.total)
    plan_rows, _warnings = _stratified_plan_rows(config, target_total)
    total = sum(row.target_valid_n for row in plan_rows)
    formulas = [
        *formulas,
        "Strata are allocated after the overall valid-response target is estimated.",
        "Proportional allocation uses each stratum's population share; equal allocation gives every stratum the same target.",
        "Weights are population share divided by planned or observed sample share when weighting is requested.",
    ]
    return (
        GroupSizes(0, total),
        "Stratified post-intervention survey confidence interval with representation planning",
        formulas,
    )


def _apply_fpc(groups: GroupSizes, config: StudyConfig) -> tuple[GroupSizes, bool]:
    if not config.apply_fpc or not config.finite_population:
        return groups, False
    total = groups.total
    adjusted_total = (config.finite_population * total) / (config.finite_population + total - 1)
    return _allocate_total(math.ceil(adjusted_total), config), True


def _allocate_total(total: int, config: StudyConfig) -> GroupSizes:
    if config.study_design in {"one_group_pre_post", "one_group_post_survey", "stratified_post_survey"}:
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
    if config.study_design in {"one_group_post_survey", "stratified_post_survey"}:
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


def _observed_groups(config: StudyConfig) -> GroupSizes:
    if config.study_design in {"one_group_pre_post", "one_group_post_survey", "stratified_post_survey"}:
        if config.study_design == "stratified_post_survey" and config.observed_total_n is None:
            strata_total = _stratified_observed_total(config)
            if strata_total:
                return GroupSizes(0, strata_total)
        if config.study_design == "one_group_post_survey" and config.observed_total_n is None:
            return GroupSizes(0, _survey_total_n_from_counts(_parse_survey_counts(config.observed_survey_counts)))
        return GroupSizes(0, int(config.observed_total_n or 0))
    if config.observed_control_n is not None and config.observed_intervention_n is not None:
        return GroupSizes(int(config.observed_control_n), int(config.observed_intervention_n))
    total = int(config.observed_total_n or 0)
    k = max(config.allocation_ratio, 1e-9)
    control = max(2, math.floor(total / (1 + k)))
    intervention = max(2, total - control)
    return GroupSizes(control, intervention)


def _has_observed_effect_information(config: StudyConfig) -> bool:
    if config.study_design == "stratified_post_survey":
        return bool(config.observed_strata_counts.strip()) or bool(_parse_survey_counts(config.observed_survey_counts)) or (
            config.observed_survey_favorable_count is not None
        ) or (
            config.survey_analysis_goal == "mean_score"
            and config.observed_survey_mean is not None
            and config.observed_survey_sd is not None
        )
    if config.study_design == "one_group_post_survey":
        return bool(_parse_survey_counts(config.observed_survey_counts)) or (
            config.observed_survey_favorable_count is not None
        ) or (
            config.survey_analysis_goal == "mean_score"
            and config.observed_survey_mean is not None
            and config.observed_survey_sd is not None
        )
    if config.study_design == "one_group_pre_post" and config.outcome_type == "binary":
        return (
            config.observed_pre_success_post_failure is not None
            and config.observed_pre_failure_post_success is not None
        )
    if config.study_design == "parallel_two_group" and config.outcome_type == "binary":
        return (
            config.observed_effect_size is not None
            or (
                config.observed_control_events is not None
                and config.observed_intervention_events is not None
            )
        )
    return config.observed_effect_size is not None


def _survey_planning_sd(config: StudyConfig) -> float:
    if config.survey_expected_sd is not None:
        return config.survey_expected_sd
    return max((config.survey_scale_max - config.survey_scale_min) / 4, 1e-9)


def _parse_survey_counts(raw: str | None) -> list[tuple[str, float | None, int, bool]]:
    if not raw or not str(raw).strip():
        return []
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PlanningError(
            "observed_survey_counts must be JSON, for example {\"1\": 2, \"2\": 4, \"3\": 10, \"4\": 18, \"5\": 26, \"NA\": 3}."
        ) from exc
    if not isinstance(payload, dict):
        raise PlanningError("observed_survey_counts must be a JSON object with category labels and counts.")
    rows: list[tuple[str, float | None, int, bool]] = []
    for label, count_value in payload.items():
        try:
            count = int(count_value)
        except (TypeError, ValueError) as exc:
            raise PlanningError("All observed_survey_counts values must be integer counts.") from exc
        if count < 0:
            raise PlanningError("observed_survey_counts cannot contain negative counts.")
        text = str(label).strip()
        missing = text.lower() in {"na", "n/a", "not applicable", "missing", "sem resposta", "nao se aplica"}
        value = None if missing else _numeric_value_from_label(text)
        rows.append((text, value, count, missing or value is None))
    rows.sort(key=lambda item: (item[3], item[1] if item[1] is not None else math.inf, item[0]))
    return rows


def _numeric_value_from_label(label: str) -> float | None:
    try:
        return float(label.replace(",", "."))
    except ValueError:
        match = re.search(r"[-+]?\d+(?:[\.,]\d+)?", label)
        if not match:
            return None
        return float(match.group(0).replace(",", "."))


def _survey_total_n_from_counts(rows: list[tuple[str, float | None, int, bool]]) -> int:
    return sum(count for _label, _value, count, _missing in rows)


def _survey_valid_n_from_counts(rows: list[tuple[str, float | None, int, bool]]) -> int:
    return sum(count for _label, _value, count, missing in rows if not missing)


def _weighted_survey_mean_sd(rows: list[tuple[str, float | None, int, bool]]) -> tuple[float | None, float | None]:
    valid = [(value, count) for _label, value, count, missing in rows if not missing and value is not None and count > 0]
    n = sum(count for _value, count in valid)
    if n <= 0:
        return None, None
    mean = sum(float(value) * count for value, count in valid) / n
    if n <= 1:
        return mean, None
    variance = sum(count * (float(value) - mean) ** 2 for value, count in valid) / (n - 1)
    return mean, math.sqrt(max(variance, 0.0))


def _parse_strata_definition(raw: str | None) -> list[StratumDefinition]:
    if not raw or not str(raw).strip():
        return []
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PlanningError(
            "strata_definition must be JSON, for example "
            "{\"age_8_10\": {\"label\": \"Age 8-10\", \"population_proportion\": 0.30}}."
        ) from exc
    if isinstance(payload, dict):
        items = list(payload.items())
    elif isinstance(payload, list):
        items = [(str(index + 1), item) for index, item in enumerate(payload)]
    else:
        raise PlanningError("strata_definition must be a JSON object or a list of strata.")
    strata: list[StratumDefinition] = []
    seen: set[str] = set()
    for fallback_id, item in items:
        if isinstance(item, dict):
            stratum_id = str(item.get("id") or fallback_id).strip()
            label = str(item.get("label") or stratum_id).strip()
            population_n = _payload_optional_int(item, ("population_n", "population", "n"))
            population_proportion = _payload_optional_float(
                item,
                ("population_proportion", "population_share", "proportion", "share"),
            )
            target_valid_n = _payload_optional_int(
                item,
                ("target_valid_n", "target_n", "planned_n", "sample_n"),
            )
        else:
            stratum_id = str(fallback_id).strip()
            label = str(fallback_id).strip()
            value = _payload_scalar_float(item, "stratum value")
            population_n = int(value) if value > 1 else None
            population_proportion = value if 0 < value <= 1 else None
            target_valid_n = None
        if not stratum_id:
            raise PlanningError("Every stratum must have a non-empty id.")
        if stratum_id in seen:
            raise PlanningError(f"Duplicate stratum id: {stratum_id}.")
        seen.add(stratum_id)
        if population_n is not None and population_n <= 0:
            raise PlanningError("population_n must be positive when provided.")
        if population_proportion is not None and population_proportion <= 0:
            raise PlanningError("population_proportion must be positive when provided.")
        if target_valid_n is not None and target_valid_n <= 0:
            raise PlanningError("target_valid_n must be positive when provided.")
        strata.append(
            StratumDefinition(
                stratum_id=stratum_id,
                label=label or stratum_id,
                population_n=population_n,
                population_proportion=population_proportion,
                target_valid_n=target_valid_n,
            )
        )
    return strata


def _payload_optional_int(payload: dict[str, Any], keys: tuple[str, ...]) -> int | None:
    for key in keys:
        if key in payload and payload[key] not in (None, ""):
            value = _payload_scalar_float(payload[key], key)
            return int(value)
    return None


def _payload_optional_float(payload: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        if key in payload and payload[key] not in (None, ""):
            return _payload_scalar_float(payload[key], key)
    return None


def _payload_scalar_float(value: Any, name: str) -> float:
    try:
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError) as exc:
        raise PlanningError(f"{name} must be numeric.") from exc


def _strata_with_population_shares(
    config: StudyConfig,
) -> tuple[list[tuple[StratumDefinition, float]], list[str]]:
    strata = _parse_strata_definition(config.strata_definition)
    warnings: list[str] = []
    if not strata:
        return [], warnings
    if config.stratified_population_known and all(item.population_proportion is not None for item in strata):
        total = sum(float(item.population_proportion or 0.0) for item in strata)
        if total <= 0:
            raise PlanningError("At least one population_proportion must be positive.")
        if abs(total - 1.0) > 0.02:
            warnings.append(
                f"Stratum proportions sum to {total:.3f}; they were normalized to 1.0."
            )
        return [(item, float(item.population_proportion or 0.0) / total) for item in strata], warnings
    if config.stratified_population_known and all(item.population_n is not None for item in strata):
        total_population = sum(int(item.population_n or 0) for item in strata)
        if total_population <= 0:
            raise PlanningError("At least one population_n must be positive.")
        return [(item, int(item.population_n or 0) / total_population) for item in strata], warnings
    share = 1 / len(strata)
    warnings.append(
        "Population composition was not fully provided, so strata are treated as equally important."
    )
    return [(item, share) for item in strata], warnings


def _stratified_plan_rows(
    config: StudyConfig,
    target_total: int,
) -> tuple[list[StratumPlanRow], list[str]]:
    strata, warnings = _strata_with_population_shares(config)
    if not strata:
        return [], warnings
    count = len(strata)
    method = config.stratified_allocation_method
    if method == "manual":
        targets = [int(item.target_valid_n or 0) for item, _share in strata]
    elif method == "equal":
        targets = [math.ceil(target_total / count) for _item, _share in strata]
    elif method == "minimum_per_stratum":
        targets = [
            max(math.ceil(target_total * share), config.stratified_min_per_stratum)
            for _item, share in strata
        ]
    else:
        targets = [math.ceil(target_total * share) for _item, share in strata]
    completion_factor = config.completion_rate * config.usable_data_rate * (1 - config.extra_buffer_rate)
    if completion_factor <= 0:
        raise PlanningError("completion, usable-data, and buffer rates make collection impossible.")
    target_sum = max(sum(targets), 1)
    rows: list[StratumPlanRow] = []
    for (item, share), target in zip(strata, targets):
        assigned = math.ceil(target / completion_factor)
        invited = math.ceil(assigned / config.response_rate)
        sample_share = target / target_sum if target_sum else 0.0
        weight = (share / sample_share) if config.stratified_use_weights and sample_share > 0 else None
        note = "manual target" if method == "manual" else f"{method.replace('_', ' ')} allocation"
        rows.append(
            StratumPlanRow(
                stratum_id=item.stratum_id,
                label=item.label,
                population_n=item.population_n,
                population_proportion=share,
                target_valid_n=target,
                assigned_needed=assigned,
                invited_needed=invited,
                response_rate=config.response_rate,
                completion_rate=config.completion_rate,
                usable_data_rate=config.usable_data_rate,
                weight=weight,
                note=note,
            )
        )
    if count > 10:
        warnings.append(
            "Many strata were defined. Crossing several demographic variables can create sparse cells and unstable weights."
        )
    if any(row.target_valid_n < config.stratified_min_per_stratum for row in rows):
        warnings.append(
            "At least one planned stratum is below the configured minimum per stratum."
        )
    if any(row.weight is not None and (row.weight < 0.5 or row.weight > 2.0) for row in rows):
        warnings.append(
            "At least one planned weight is outside 0.5 to 2.0; this can make weighted estimates unstable."
        )
    return rows, warnings


def _parse_observed_strata_counts(raw: str | None) -> dict[str, dict[str, Any]]:
    if not raw or not str(raw).strip():
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PlanningError(
            "observed_strata_counts must be JSON, for example "
            "{\"age_8_10\": {\"counts\": {\"1\": 1, \"4\": 12, \"5\": 18, \"NA\": 2}}}."
        ) from exc
    if isinstance(payload, list):
        items = []
        for index, item in enumerate(payload):
            if not isinstance(item, dict):
                raise PlanningError("Each observed stratum list item must be an object.")
            items.append((str(item.get("id") or index + 1), item))
    elif isinstance(payload, dict):
        items = list(payload.items())
    else:
        raise PlanningError("observed_strata_counts must be a JSON object or list.")
    observed: dict[str, dict[str, Any]] = {}
    for stratum_id, item in items:
        key = str(stratum_id).strip()
        if not key:
            raise PlanningError("Every observed stratum must have a non-empty id.")
        if isinstance(item, dict):
            observed[key] = dict(item)
        else:
            observed[key] = {"valid_n": item}
    return observed


def _stratified_observed_total(config: StudyConfig) -> int:
    observed = _parse_observed_strata_counts(config.observed_strata_counts)
    total = 0
    for item in observed.values():
        counts_payload = item.get("counts")
        if isinstance(counts_payload, dict):
            rows = _parse_survey_counts(json.dumps(counts_payload))
            total += _survey_total_n_from_counts(rows)
        else:
            total += int(_payload_optional_int(item, ("valid_n", "valid", "n", "observed_valid_n")) or 0)
            total += int(_payload_optional_int(item, ("missing_n", "missing", "na")) or 0)
    return total


def _combine_mean_sd(components: list[tuple[int, float, float | None]]) -> tuple[float | None, float | None]:
    total = sum(n for n, _mean, _sd in components)
    if total <= 0:
        return None, None
    mean = sum(n * value for n, value, _sd in components) / total
    if total <= 1:
        return mean, None
    sum_squares = 0.0
    for n, value, sd in components:
        if n <= 0:
            continue
        if sd is not None and n > 1:
            sum_squares += (n - 1) * sd**2
        sum_squares += n * (value - mean) ** 2
    return mean, math.sqrt(max(sum_squares / (total - 1), 0.0))


def _stratified_observed_rows_and_survey(
    config: StudyConfig,
    plan_rows: list[StratumPlanRow],
    alpha: float,
) -> tuple[list[StratumObservedRow], SurveyAnalysis, list[str]]:
    strata, warnings = _strata_with_population_shares(config)
    observed = _parse_observed_strata_counts(config.observed_strata_counts)
    plan_by_id = {row.stratum_id: row for row in plan_rows}
    expected_ids = {item.stratum_id for item, _share in strata}
    unknown_ids = sorted(set(observed) - expected_ids)
    if unknown_ids:
        warnings.append(
            "Observed data contain strata not present in strata_definition: " + ", ".join(unknown_ids) + "."
        )
    total_valid = 0
    total_missing = 0
    total_favorable: int | None = 0
    aggregate_counts: dict[str, int] = {}
    mean_components: list[tuple[int, float, float | None]] = []
    raw_rows: list[dict[str, Any]] = []
    for definition, expected_share in strata:
        item = observed.get(definition.stratum_id, {})
        counts_payload = item.get("counts") if isinstance(item, dict) else None
        counts_rows = _parse_survey_counts(json.dumps(counts_payload)) if isinstance(counts_payload, dict) else []
        if counts_rows:
            valid_n = _survey_valid_n_from_counts(counts_rows)
            missing_n = _survey_total_n_from_counts(counts_rows) - valid_n
            favorable_count = sum(
                count
                for _label, value, count, missing in counts_rows
                if not missing and value is not None and value >= config.survey_favorable_threshold
            )
            mean, sd = _weighted_survey_mean_sd(counts_rows)
            for label, _value, count, _missing in counts_rows:
                aggregate_counts[label] = aggregate_counts.get(label, 0) + count
        else:
            valid_n = int(_payload_optional_int(item, ("valid_n", "valid", "n", "observed_valid_n")) or 0)
            missing_n = int(_payload_optional_int(item, ("missing_n", "missing", "na")) or 0)
            favorable_count = _payload_optional_int(
                item,
                ("favorable_count", "favorable", "positive", "observed_favorable_count"),
            )
            mean = _payload_optional_float(item, ("mean", "observed_mean", "survey_mean"))
            sd = _payload_optional_float(item, ("sd", "observed_sd", "survey_sd"))
        if favorable_count is None:
            total_favorable = None
        elif total_favorable is not None:
            total_favorable += favorable_count
        if mean is not None and valid_n > 0:
            mean_components.append((valid_n, mean, sd))
        total_valid += valid_n
        total_missing += missing_n
        raw_rows.append(
            {
                "definition": definition,
                "expected_share": expected_share,
                "valid_n": valid_n,
                "missing_n": missing_n,
                "favorable_count": favorable_count,
                "mean": mean,
            }
        )
    observed_rows: list[StratumObservedRow] = []
    for item in raw_rows:
        definition = item["definition"]
        expected_share = item["expected_share"]
        valid_n = int(item["valid_n"])
        missing_n = int(item["missing_n"])
        observed_share = valid_n / total_valid if total_valid > 0 else None
        ratio = observed_share / expected_share if observed_share is not None and expected_share > 0 else None
        weight = expected_share / observed_share if config.stratified_use_weights and observed_share else None
        favorable_count = item["favorable_count"]
        favorable_proportion = (favorable_count / valid_n) if favorable_count is not None and valid_n > 0 else None
        ci_low = ci_high = None
        if favorable_count is not None and valid_n > 0:
            ci_low, ci_high = _wilson_ci(favorable_count, valid_n, alpha)
        target = plan_by_id.get(definition.stratum_id)
        if valid_n == 0:
            status = "missing"
            note = "no observed valid responses for this stratum"
        elif target and valid_n < target.target_valid_n:
            status = "under target"
            note = f"{target.target_valid_n - valid_n} more valid responses needed for the planned stratum target"
        elif ratio is not None and ratio < 0.80:
            status = "under-represented"
            note = "observed share is below 80% of expected population share"
        elif ratio is not None and ratio > 1.25:
            status = "over-represented"
            note = "observed share is above 125% of expected population share"
        else:
            status = "ok"
            note = "representation is within the broad 80% to 125% check"
        observed_rows.append(
            StratumObservedRow(
                stratum_id=definition.stratum_id,
                label=definition.label,
                expected_proportion=expected_share,
                observed_valid_n=valid_n,
                observed_missing_n=missing_n,
                observed_share=observed_share,
                representation_ratio=ratio,
                weight=weight,
                favorable_count=favorable_count,
                favorable_proportion=favorable_proportion,
                favorable_ci_low=ci_low,
                favorable_ci_high=ci_high,
                mean=item["mean"],
                status=status,
                note=note,
            )
        )
    category_rows: list[SurveyCategoryRow] = []
    aggregate_rows = _parse_survey_counts(json.dumps(aggregate_counts)) if aggregate_counts else []
    for label, value, count, missing in aggregate_rows:
        denominator = (total_valid + total_missing) if missing else max(total_valid, 1)
        low, high = _wilson_ci(count, denominator, alpha)
        category_rows.append(
            SurveyCategoryRow(
                label=label,
                count=count,
                proportion=count / denominator if denominator else 0.0,
                ci_low=low,
                ci_high=high,
                favorable=(not missing and value is not None and value >= config.survey_favorable_threshold),
                missing=missing,
            )
        )
    favorable_proportion = None
    favorable_ci_low = None
    favorable_ci_high = None
    target_reached = None
    margin_of_error = None
    if total_favorable is not None and total_valid > 0:
        favorable_proportion = total_favorable / total_valid
        favorable_ci_low, favorable_ci_high = _wilson_ci(total_favorable, total_valid, alpha)
        margin_of_error = max(favorable_proportion - favorable_ci_low, favorable_ci_high - favorable_proportion)
        target_reached = favorable_ci_low >= config.survey_target_proportion
    mean, sd = _combine_mean_sd(mean_components)
    mean_ci_low = mean_ci_high = None
    target_mean_reached = None
    if mean is not None and sd is not None and total_valid > 1:
        mean_ci_low, mean_ci_high = _mean_ci(mean, sd, total_valid, alpha)
        if config.survey_target_mean is not None:
            target_mean_reached = mean_ci_low >= config.survey_target_mean
    survey = SurveyAnalysis(
        confidence_level=1 - alpha,
        valid_n=total_valid,
        missing_n=total_missing,
        favorable_count=total_favorable,
        favorable_proportion=favorable_proportion,
        favorable_ci_low=favorable_ci_low,
        favorable_ci_high=favorable_ci_high,
        target_proportion=config.survey_target_proportion,
        target_reached=target_reached,
        margin_of_error=margin_of_error,
        mean=mean,
        sd=sd,
        mean_ci_low=mean_ci_low,
        mean_ci_high=mean_ci_high,
        target_mean=config.survey_target_mean,
        target_mean_reached=target_mean_reached,
        category_rows=category_rows,
    )
    return observed_rows, survey, warnings


def _wilson_ci(count: int, total: int, alpha: float) -> tuple[float, float]:
    if total <= 0:
        return 0.0, 0.0
    z = _z_alpha(alpha, "two_sided")
    p = count / total
    denominator = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denominator
    half = z * math.sqrt((p * (1 - p) + z**2 / (4 * total)) / total) / denominator
    return _clamp(center - half, 0.0, 1.0), _clamp(center + half, 0.0, 1.0)


def _mean_ci(mean: float, sd: float, total: int, alpha: float) -> tuple[float, float]:
    z = _z_alpha(alpha, "two_sided")
    half = z * sd / math.sqrt(total)
    return mean - half, mean + half


def _observed_analysis(config: StudyConfig, z_alpha: float) -> ObservedAnalysis | None:
    if config.analysis_mode != "evaluate":
        return None
    groups = _observed_groups(config)
    if not _has_observed_effect_information(config):
        return _sample_capacity_analysis(config, groups)
    if config.study_design == "stratified_post_survey" and config.observed_strata_counts.strip():
        return _stratified_survey_observed_analysis(config, groups)
    if config.study_design in {"one_group_post_survey", "stratified_post_survey"}:
        return _survey_observed_analysis(config, groups)
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


def _survey_observed_analysis(config: StudyConfig, groups: GroupSizes) -> ObservedAnalysis:
    rows = _parse_survey_counts(config.observed_survey_counts)
    counted_total = _survey_total_n_from_counts(rows)
    observed_total = int(config.observed_total_n or counted_total)
    valid_n = _survey_valid_n_from_counts(rows) if rows else observed_total
    missing_n = max(0, observed_total - valid_n)
    alpha = config.alpha / config.primary_comparisons

    category_rows: list[SurveyCategoryRow] = []
    for label, value, count, missing in rows:
        denominator = observed_total if missing else max(valid_n, 1)
        low, high = _wilson_ci(count, denominator, alpha)
        category_rows.append(
            SurveyCategoryRow(
                label=label,
                count=count,
                proportion=count / denominator if denominator else 0.0,
                ci_low=low,
                ci_high=high,
                favorable=(not missing and value is not None and value >= config.survey_favorable_threshold),
                missing=missing,
            )
        )

    favorable_count: int | None = None
    favorable_proportion: float | None = None
    favorable_ci_low: float | None = None
    favorable_ci_high: float | None = None
    target_reached: bool | None = None
    margin_of_error: float | None = None
    mean: float | None = None
    sd: float | None = None
    mean_ci_low: float | None = None
    mean_ci_high: float | None = None
    target_mean_reached: bool | None = None

    counted_favorable = sum(
        count
        for _label, value, count, missing in rows
        if not missing and value is not None and value >= config.survey_favorable_threshold
    )
    if rows or config.observed_survey_favorable_count is not None:
        favorable_count = (
            int(config.observed_survey_favorable_count)
            if config.observed_survey_favorable_count is not None
            else counted_favorable
        )
        valid_denominator = max(valid_n, 1)
        favorable_proportion = favorable_count / valid_denominator
        favorable_ci_low, favorable_ci_high = _wilson_ci(favorable_count, valid_denominator, alpha)
        margin_of_error = max(favorable_proportion - favorable_ci_low, favorable_ci_high - favorable_proportion)
        target_reached = favorable_ci_low >= config.survey_target_proportion

    counted_mean, counted_sd = _weighted_survey_mean_sd(rows)
    if counted_mean is not None:
        mean = counted_mean
        sd = counted_sd
    elif config.observed_survey_mean is not None and config.observed_survey_sd is not None:
        mean = config.observed_survey_mean
        sd = config.observed_survey_sd
    if mean is not None and sd is not None and valid_n > 1:
        mean_ci_low, mean_ci_high = _mean_ci(mean, sd, valid_n, alpha)
        if config.survey_target_mean is not None:
            target_mean_reached = mean_ci_low >= config.survey_target_mean

    if config.survey_analysis_goal == "mean_score" and mean is not None:
        observed_effect = mean
    else:
        observed_effect = favorable_proportion

    survey = SurveyAnalysis(
        confidence_level=1 - alpha,
        valid_n=valid_n,
        missing_n=missing_n,
        favorable_count=favorable_count,
        favorable_proportion=favorable_proportion,
        favorable_ci_low=favorable_ci_low,
        favorable_ci_high=favorable_ci_high,
        target_proportion=config.survey_target_proportion,
        target_reached=target_reached,
        margin_of_error=margin_of_error,
        mean=mean,
        sd=sd,
        mean_ci_low=mean_ci_low,
        mean_ci_high=mean_ci_high,
        target_mean=config.survey_target_mean,
        target_mean_reached=target_mean_reached,
        category_rows=category_rows,
    )
    method_notes = [
        "This is a descriptive post-intervention survey analysis, not evidence of change caused by the intervention.",
        "NA or nonnumeric categories are excluded from the valid denominator and reported as missing/non-applicable.",
        "Favorable-response confidence intervals use Wilson intervals; score means use a normal-approximate confidence interval.",
    ]
    if config.survey_analysis_goal == "favorable_proportion" and favorable_proportion is not None:
        method_notes.append(
            f"Claim check: the lower confidence bound must be at least {config.survey_target_proportion:.1%} to say that at least that share of users gave a favorable answer."
        )
    if config.survey_analysis_goal == "mean_score" and config.survey_target_mean is not None:
        method_notes.append(
            f"Mean-score claim check: the lower confidence bound must be at least {config.survey_target_mean:.2f}."
        )
    return ObservedAnalysis(
        observed_control=0,
        observed_intervention=observed_total,
        observed_total=observed_total,
        observed_effect_size=observed_effect,
        observed_control_rate=None,
        observed_intervention_rate=favorable_proportion,
        z_statistic=None,
        p_value=None,
        achieved_power=None,
        method="One-group post-intervention survey confidence interval",
        method_notes=method_notes,
        planned_targets=_planned_targets(config, GroupSizes(0, observed_total)),
        survey_analysis=survey,
    )


def _stratified_survey_observed_analysis(config: StudyConfig, groups: GroupSizes) -> ObservedAnalysis:
    alpha = config.alpha / config.primary_comparisons
    plan_rows: list[StratumPlanRow] = []
    if config.had_planned_sample and config.planned_total_n:
        plan_rows, _warnings = _stratified_plan_rows(config, config.planned_total_n)
    observed_rows, survey, warnings = _stratified_observed_rows_and_survey(config, plan_rows, alpha)
    observed_total = survey.valid_n + survey.missing_n
    observed_effect = survey.mean if config.survey_analysis_goal == "mean_score" else survey.favorable_proportion
    method_notes = [
        "This is a descriptive stratified opinion survey analysis, not evidence that the intervention caused the opinions.",
        "Representation status compares each observed stratum share with the expected population share.",
        "Weights are diagnostic unless you explicitly use a weighted estimator in the final survey analysis.",
    ]
    if warnings:
        method_notes.extend(warnings)
    if any(row.status in {"missing", "under target", "under-represented"} for row in observed_rows):
        method_notes.append(
            "At least one stratum needs attention before making a broad population-representation claim."
        )
    return ObservedAnalysis(
        observed_control=0,
        observed_intervention=observed_total,
        observed_total=observed_total or groups.total,
        observed_effect_size=observed_effect,
        observed_control_rate=None,
        observed_intervention_rate=survey.favorable_proportion,
        z_statistic=None,
        p_value=None,
        achieved_power=None,
        method="Stratified post-intervention survey representation analysis",
        method_notes=method_notes,
        planned_targets=_planned_targets(config, GroupSizes(0, observed_total or groups.total)),
        survey_analysis=survey,
    )


def _stratified_survey_analysis(
    config: StudyConfig,
    z_alpha: float,
    design_adjusted: GroupSizes,
    observed_analysis: ObservedAnalysis | None,
) -> StratifiedSurveyAnalysis | None:
    if config.study_design != "stratified_post_survey":
        return None
    warnings: list[str] = []
    plan_rows: list[StratumPlanRow] = []
    target_total = 0
    if config.analysis_mode == "plan":
        target_total = design_adjusted.total
        plan_rows, row_warnings = _stratified_plan_rows(config, target_total)
        warnings.extend(row_warnings)
    elif config.had_planned_sample and config.planned_total_n:
        target_total = int(config.planned_total_n)
        plan_rows, row_warnings = _stratified_plan_rows(config, target_total)
        warnings.extend(row_warnings)
    elif config.stratified_target_total:
        target_total = int(config.stratified_target_total)
        plan_rows, row_warnings = _stratified_plan_rows(config, target_total)
        warnings.extend(row_warnings)
    observed_rows: list[StratumObservedRow] = []
    if config.analysis_mode == "evaluate" and config.observed_strata_counts.strip():
        observed_rows, _survey, observed_warnings = _stratified_observed_rows_and_survey(
            config,
            plan_rows,
            config.alpha / config.primary_comparisons,
        )
        warnings.extend(observed_warnings)
    effective_rate = config.response_rate * config.completion_rate * config.usable_data_rate * (1 - config.extra_buffer_rate)
    return StratifiedSurveyAnalysis(
        allocation_method=config.stratified_allocation_method,
        confidence_level=1 - (config.alpha / config.primary_comparisons),
        target_total_valid=sum(row.target_valid_n for row in plan_rows) if plan_rows else target_total,
        assigned_total=sum(row.assigned_needed for row in plan_rows),
        invited_total=sum(row.invited_needed for row in plan_rows),
        effective_data_rate=effective_rate,
        use_weights=config.stratified_use_weights,
        plan_rows=plan_rows,
        observed_rows=observed_rows,
        warnings=warnings,
    )


def _sample_capacity_analysis(config: StudyConfig, groups: GroupSizes) -> ObservedAnalysis:
    if config.study_design in {"one_group_post_survey", "stratified_post_survey"}:
        return _survey_capacity_analysis(config, groups)
    capacity_groups = _capacity_group_options(config, groups)
    return ObservedAnalysis(
        observed_control=groups.control,
        observed_intervention=groups.intervention,
        observed_total=groups.total,
        observed_effect_size=None,
        observed_control_rate=None,
        observed_intervention_rate=None,
        z_statistic=None,
        p_value=None,
        achieved_power=None,
        method="Sample-size capacity analysis",
        method_notes=[
            "Only sample size was entered, so there is no unique p-value or achieved power.",
            "The capacity table shows the minimum effect that this sample could detect for common alpha and power combinations.",
        ],
        planned_targets=_planned_targets(config, groups),
        capacity_rows=[
            row
            for option in capacity_groups
            for row in _capacity_rows(config, option)
        ],
    )


def _survey_capacity_analysis(config: StudyConfig, groups: GroupSizes) -> ObservedAnalysis:
    total = groups.total
    alpha = config.alpha / config.primary_comparisons
    p = _clamp(config.survey_expected_proportion, 0.001, 0.999)
    z = _z_alpha(alpha, "two_sided")
    proportion_margin = z * math.sqrt(p * (1 - p) / max(total, 1)) if total else None
    sd = _survey_planning_sd(config)
    mean_margin = z * sd / math.sqrt(max(total, 1)) if total else None
    survey = SurveyAnalysis(
        confidence_level=1 - alpha,
        valid_n=total,
        missing_n=0,
        favorable_count=None,
        favorable_proportion=None,
        favorable_ci_low=None,
        favorable_ci_high=None,
        target_proportion=config.survey_target_proportion,
        target_reached=None,
        margin_of_error=proportion_margin if config.survey_analysis_goal == "favorable_proportion" else mean_margin,
        mean=None,
        sd=sd if config.survey_analysis_goal == "mean_score" else None,
        mean_ci_low=None,
        mean_ci_high=None,
        target_mean=config.survey_target_mean,
        target_mean_reached=None,
        category_rows=[],
    )
    note = (
        f"With {total} valid responses, the approximate {survey.confidence_level:.0%} margin is "
        f"{proportion_margin:.1%} around an expected favorable proportion of {p:.1%}."
        if config.survey_analysis_goal == "favorable_proportion" and proportion_margin is not None
        else f"With {total} valid responses, the approximate {survey.confidence_level:.0%} mean margin is {mean_margin:.3f} score points using SD={sd:.3f}."
    )
    return ObservedAnalysis(
        observed_control=0,
        observed_intervention=total,
        observed_total=total,
        observed_effect_size=None,
        observed_control_rate=None,
        observed_intervention_rate=None,
        z_statistic=None,
        p_value=None,
        achieved_power=None,
        method="Post-intervention survey sample-size capacity analysis",
        method_notes=[
            "Only the achieved survey sample size was entered, so there is no observed distribution to evaluate.",
            note,
        ],
        planned_targets=_planned_targets(config, groups),
        survey_analysis=survey,
    )


def _capacity_group_options(config: StudyConfig, groups: GroupSizes) -> list[GroupSizes]:
    if config.study_design in {"one_group_pre_post", "one_group_post_survey", "stratified_post_survey"}:
        return [groups]
    if config.observed_control_n is not None and config.observed_intervention_n is not None:
        return [groups]
    total = int(config.observed_total_n or groups.total)
    ratios = [config.allocation_ratio, 1.0, 2.0, 0.5]
    options: list[GroupSizes] = []
    seen: set[tuple[int, int]] = set()
    for ratio in ratios:
        k = max(ratio, 1e-9)
        control = max(2, math.floor(total / (1 + k)))
        intervention = max(2, total - control)
        key = (control, intervention)
        if key not in seen and control + intervention == total:
            options.append(GroupSizes(control, intervention))
            seen.add(key)
    return options


def _capacity_rows(config: StudyConfig, groups: GroupSizes) -> list[CapacityRow]:
    rows: list[CapacityRow] = []
    for alpha, desired_power in ((0.10, 0.80), (0.05, 0.80), (0.05, 0.90), (0.01, 0.80), (0.01, 0.90)):
        effect = _minimum_detectable_effect(config, groups, alpha, desired_power)
        rows.append(
            CapacityRow(
                label=f"p < {alpha:.2f}, power {desired_power:.0%}",
                alpha=alpha,
                power=desired_power,
                effect_size=effect,
                effect_label=_effect_requirement_label(config, effect),
                control=groups.control,
                intervention=groups.intervention,
                total=groups.total,
                note=_capacity_note(config, groups),
            )
        )
    for effect in _common_effect_values(config):
        for alpha in (0.05, 0.10):
            achieved = _power_for_effect(config, groups, alpha, effect)
            rows.append(
                CapacityRow(
                    label=f"Power if {_effect_short_label(config, effect)}, p < {alpha:.2f}",
                    alpha=alpha,
                    power=achieved,
                    effect_size=effect,
                    effect_label=f"power ~= {achieved:.1%}",
                    control=groups.control,
                    intervention=groups.intervention,
                    total=groups.total,
                    note=_capacity_note(config, groups),
                )
            )
    for effect in _common_effect_values(config):
        for desired_power in (0.80, 0.90):
            alpha_needed = _alpha_for_effect_and_power(config, groups, effect, desired_power)
            rows.append(
                CapacityRow(
                    label=f"Alpha needed for {_effect_short_label(config, effect)}, power {desired_power:.0%}",
                    alpha=alpha_needed if alpha_needed is not None else 0.0,
                    power=desired_power,
                    effect_size=effect,
                    effect_label=_alpha_requirement_label(alpha_needed),
                    control=groups.control,
                    intervention=groups.intervention,
                    total=groups.total,
                    note=_capacity_note(config, groups),
                )
            )
    return rows


def _common_effect_values(config: StudyConfig) -> list[float]:
    if config.outcome_type == "binary":
        values = [0.05, 0.10, 0.15, 0.20]
        if config.study_design == "parallel_two_group":
            upper = _capacity_effect_upper(config)
            return [value for value in values if value < upper]
        return values
    return [0.20, 0.50, 0.80]


def _power_for_effect(config: StudyConfig, groups: GroupSizes, alpha: float, effect: float) -> float:
    z_alpha = _z_alpha(alpha / config.primary_comparisons, config.alternative)
    effective_groups = _effective_groups_for_capacity(groups, config)
    if config.study_design == "one_group_pre_post":
        z_beta = math.sqrt(max(effective_groups.total, 1)) * effect - z_alpha
        return _clamp(NORMAL.cdf(z_beta), 0.0, 1.0)
    k = _observed_ratio(config, effective_groups)
    if config.study_design == "pretest_posttest_control":
        base = math.sqrt(effective_groups.control / (1 + 1 / k))
        efficiency_gain = 1 / math.sqrt(max(0.05, 1 - config.pre_post_correlation**2))
        z_beta = base * effect * efficiency_gain - z_alpha
        return _clamp(NORMAL.cdf(z_beta), 0.0, 1.0)
    if config.outcome_type == "continuous":
        z_beta = math.sqrt(effective_groups.control / (1 + 1 / k)) * effect - z_alpha
        return _clamp(NORMAL.cdf(z_beta), 0.0, 1.0)
    p0 = _clamp(config.proportion_control, 0.001, 0.999)
    p1 = _clamp(p0 + effect, 0.001, 0.999)
    diff = abs(p1 - p0)
    p_bar = (p0 + p1) / 2
    pooled = max((1 + 1 / k) * p_bar * (1 - p_bar), 1e-12)
    unpooled = max(p0 * (1 - p0) + p1 * (1 - p1) / k, 1e-12)
    z_beta = (math.sqrt(effective_groups.control) * diff - z_alpha * math.sqrt(pooled)) / math.sqrt(unpooled)
    return _clamp(NORMAL.cdf(z_beta), 0.0, 1.0)


def _alpha_for_effect_and_power(
    config: StudyConfig,
    groups: GroupSizes,
    effect: float,
    desired_power: float,
) -> float | None:
    z_power = NORMAL.inv_cdf(desired_power)
    effective_groups = _effective_groups_for_capacity(groups, config)
    if config.study_design == "one_group_pre_post":
        z_alpha = math.sqrt(max(effective_groups.total, 1)) * effect - z_power
    else:
        k = _observed_ratio(config, effective_groups)
        if config.study_design == "pretest_posttest_control":
            base = math.sqrt(effective_groups.control / (1 + 1 / k))
            efficiency_gain = 1 / math.sqrt(max(0.05, 1 - config.pre_post_correlation**2))
            z_alpha = base * effect * efficiency_gain - z_power
        elif config.outcome_type == "continuous":
            z_alpha = math.sqrt(effective_groups.control / (1 + 1 / k)) * effect - z_power
        else:
            p0 = _clamp(config.proportion_control, 0.001, 0.999)
            p1 = _clamp(p0 + effect, 0.001, 0.999)
            diff = abs(p1 - p0)
            p_bar = (p0 + p1) / 2
            pooled = max((1 + 1 / k) * p_bar * (1 - p_bar), 1e-12)
            unpooled = max(p0 * (1 - p0) + p1 * (1 - p1) / k, 1e-12)
            z_alpha = (math.sqrt(effective_groups.control) * diff - z_power * math.sqrt(unpooled)) / math.sqrt(pooled)
    if z_alpha <= 0:
        return None
    tail = 1 - NORMAL.cdf(z_alpha)
    alpha = (2 * tail) if config.alternative == "two_sided" else tail
    if not 0 < alpha <= 1:
        return None
    return alpha


def _effective_groups_for_capacity(groups: GroupSizes, config: StudyConfig) -> GroupSizes:
    design_effect = _design_effect(config)
    if design_effect <= 1:
        return groups
    if config.study_design in {"one_group_pre_post", "one_group_post_survey", "stratified_post_survey"}:
        return GroupSizes(0, max(2, math.floor(groups.intervention / design_effect)))
    return GroupSizes(
        max(2, math.floor(groups.control / design_effect)),
        max(2, math.floor(groups.intervention / design_effect)),
    )


def _effect_short_label(config: StudyConfig, effect: float) -> str:
    if config.outcome_type == "binary":
        return f"effect={effect:.2f}"
    return f"d={effect:.2f}"


def _alpha_requirement_label(alpha: float | None) -> str:
    if alpha is None:
        return "not achievable with alpha <= 1.00"
    return f"requires p threshold about {alpha:.3f}"


def _minimum_detectable_effect(
    config: StudyConfig,
    groups: GroupSizes,
    alpha: float,
    desired_power: float,
) -> float | None:
    upper = _capacity_effect_upper(config)
    z_alpha = _z_alpha(alpha / config.primary_comparisons, config.alternative)

    def fits(effect: float) -> bool:
        required = _required_groups_for_power(
            config,
            effect,
            groups,
            z_alpha,
            desired_power,
            None,
            None,
        )
        required = _cluster_adjusted_target(required, config)
        return required.control <= groups.control and required.intervention <= groups.intervention

    if groups.total <= 1 or not fits(upper):
        return None
    low = 1e-6
    high = upper
    for _ in range(70):
        midpoint = (low + high) / 2
        if fits(midpoint):
            high = midpoint
        else:
            low = midpoint
    return high


def _capacity_effect_upper(config: StudyConfig) -> float:
    if config.study_design == "parallel_two_group" and config.outcome_type == "binary":
        p0 = _clamp(config.proportion_control, 0.001, 0.999)
        return max(p0, 1 - p0) - 1e-6
    if config.study_design == "one_group_pre_post" and config.outcome_type == "binary":
        return 0.999
    return 3.0


def _effect_requirement_label(config: StudyConfig, effect: float | None) -> str:
    if effect is None:
        return "outside feasible range"
    if config.study_design == "parallel_two_group" and config.outcome_type == "binary":
        p0 = _clamp(config.proportion_control, 0.001, 0.999)
        p1 = _clamp(p0 + effect, 0.001, 0.999)
        return f"proportion difference >= {effect:.3f} ({p0:.1%} to {p1:.1%})"
    if config.study_design == "one_group_pre_post" and config.outcome_type == "binary":
        return f"net paired change >= {effect:.3f}"
    return f"d >= {effect:.3f}"


def _capacity_note(config: StudyConfig, groups: GroupSizes) -> str:
    if config.study_design == "stratified_post_survey":
        return "stratified post-intervention survey; evaluates opinion precision and demographic representation"
    if config.study_design == "one_group_post_survey":
        return "one post-intervention survey; estimates opinion precision, not intervention causality"
    if config.study_design == "one_group_pre_post":
        return "same people measured before and after"
    if config.study_design == "pretest_posttest_control":
        return (
            f"allocation {groups.intervention}:{groups.control}; "
            f"uses pre/post correlation {config.pre_post_correlation:.2f}"
        )
    if config.outcome_type == "binary":
        return (
            f"allocation {groups.intervention}:{groups.control}; "
            f"uses baseline rate {config.proportion_control:.1%}"
        )
    return f"allocation {groups.intervention}:{groups.control}; two independent groups"


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
    if config.study_design in {"one_group_post_survey", "stratified_post_survey"}:
        if config.survey_analysis_goal == "mean_score":
            sd = _survey_planning_sd(config)
            total = math.ceil((z_required * sd / config.survey_mean_margin_of_error) ** 2)
        else:
            p = control_rate if control_rate is not None else config.survey_expected_proportion
            total = math.ceil((z_required**2) * p * (1 - p) / config.survey_margin_of_error**2)
        return GroupSizes(0, max(2, total))
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
    if config.study_design in {"one_group_post_survey", "stratified_post_survey"}:
        return _required_groups_for_z(
            config,
            effect_size,
            observed_groups,
            z_alpha,
            control_rate,
            intervention_rate,
        )
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
    if config.study_design in {"one_group_pre_post", "one_group_post_survey", "stratified_post_survey"}:
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
    if config.study_design in {"one_group_post_survey", "stratified_post_survey"}:
        warnings.append(
            "Post-intervention opinion surveys estimate what respondents report; without pre-test or control data they cannot show that the intervention caused the opinion."
        )
        if config.survey_analysis_goal == "mean_score" and config.survey_expected_sd is None:
            warnings.append(
                "No expected survey SD was entered, so planning uses one quarter of the scale range as a rough default."
            )
    if config.study_design == "stratified_post_survey":
        warnings.append(
            "Stratified opinion surveys improve representation checks, but strata must be defined before recruitment and should be mutually exclusive and exhaustive."
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
    elif config.study_design == "one_group_pre_post":
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
    elif config.study_design == "one_group_post_survey":
        suggestions.append(
            "Use the post-intervention survey path when the claim is about users' reported opinions after using the intervention, such as MEEGA+ usability or experience items."
        )
        suggestions.append(
            "For Likert or star items, report the full distribution and use the favorable-response confidence interval for claims like 'at least 70% agreed'."
        )
        suggestions.append(
            "Treat NA and missing answers separately from valid opinions; a high NA rate is a measurement problem, not just a smaller sample."
        )
    else:
        suggestions.append(
            "Use the stratified survey path when you want an opinion claim to represent known demographic classes such as age bands, school type, region, experience level, or gender."
        )
        suggestions.append(
            "Define strata before data collection, keep them mutually exclusive, and avoid crossing so many demographics that each cell becomes tiny."
        )
        suggestions.append(
            "If a stratum is under-represented, targeted recruitment is usually better than only reporting an overall histogram."
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
        if observed_analysis.observed_effect_size is None:
            if observed_analysis.survey_analysis:
                survey = observed_analysis.survey_analysis
                if survey.margin_of_error is not None:
                    suggestions.append(
                        f"Only survey sample size was entered. At about {survey.confidence_level:.0%} confidence, the current approximate margin is {survey.margin_of_error:.3f}."
                    )
                return suggestions
            suggestions.append(
                "Only the achieved sample size was entered. The capacity table reports minimum detectable effects for common p-value and power standards instead of a single p-value."
            )
            if observed_analysis.capacity_rows:
                reference = next(
                    (
                        row
                        for row in observed_analysis.capacity_rows
                        if abs(row.alpha - 0.05) < 1e-9 and abs(row.power - 0.80) < 1e-9
                    ),
                    observed_analysis.capacity_rows[0],
                )
                suggestions.append(
                    f"For the common p < {reference.alpha:.2f} and power {reference.power:.0%} target, this sample can detect about {reference.effect_label}."
                )
            return suggestions
        if observed_analysis.survey_analysis:
            survey = observed_analysis.survey_analysis
            if survey.target_reached is True:
                suggestions.append(
                    "The lower confidence bound reaches the target favorable proportion, so the descriptive survey claim is supported for respondents."
                )
            elif survey.target_reached is False:
                suggestions.append(
                    "The favorable proportion estimate may be high, but the lower confidence bound does not reach the target. Use a weaker claim or collect more valid survey responses."
                )
            if survey.target_mean_reached is True:
                suggestions.append(
                    "The lower confidence bound reaches the target mean score."
                )
            elif survey.target_mean_reached is False:
                suggestions.append(
                    "The mean score estimate does not clear the target once uncertainty is considered."
                )
            if survey.missing_n > 0:
                suggestions.append(
                    f"{survey.missing_n} responses were missing or NA. Report this separately from the opinion percentages."
                )
            return suggestions
        assert observed_analysis.p_value is not None
        assert observed_analysis.achieved_power is not None
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
            assert observed_analysis.observed_effect_size is not None
            if observed_analysis.observed_effect_size < config.planned_effect_size:
                suggestions.append(
                    "The observed effect is smaller than the planned effect. Even a study with the planned sample can miss conventional thresholds when the real effect is smaller than expected."
                )
            else:
                suggestions.append(
                    "The observed effect is at least as large as the planned effect. If thresholds were not reached, sample size, allocation, or attrition are likely limiting factors."
                )
    return suggestions


def _stratified_survey_suggestions(
    config: StudyConfig,
    analysis: StratifiedSurveyAnalysis,
) -> list[str]:
    suggestions: list[str] = []
    if config.analysis_mode == "plan" and analysis.plan_rows:
        suggestions.append(
            "For stratified recruitment, monitor each stratum separately during data collection rather than waiting for the final total."
        )
        if config.stratified_allocation_method == "proportional":
            suggestions.append(
                "Proportional allocation is efficient for the overall estimate, but small demographic groups may receive very small samples."
            )
        elif config.stratified_allocation_method == "equal":
            suggestions.append(
                "Equal allocation gives better visibility to smaller strata, but weighted reporting is important if the population shares differ."
            )
        elif config.stratified_allocation_method == "minimum_per_stratum":
            suggestions.append(
                "The minimum-per-stratum rule protects subgroup visibility; check the total because it can exceed the original overall target."
            )
    weak_rows = [
        row
        for row in analysis.observed_rows
        if row.status in {"missing", "under target", "under-represented"}
    ]
    if weak_rows:
        labels = ", ".join(row.label for row in weak_rows[:5])
        suggestions.append(
            f"Representation needs attention in: {labels}. Collect more responses from these strata or qualify the population claim."
        )
    large_weights = [
        row
        for row in analysis.observed_rows
        if row.weight is not None and (row.weight < 0.5 or row.weight > 2.0)
    ]
    if large_weights:
        suggestions.append(
            "Some observed weights are outside 0.5 to 2.0. Treat weighted estimates cautiously and report the unweighted stratum table."
        )
    return suggestions


def _build_sensitivity(config: StudyConfig) -> list[SensitivityRow]:
    rows: list[SensitivityRow] = []
    if config.analysis_mode != "plan":
        return rows
    variants: list[tuple[str, StudyConfig]] = []
    if config.study_design in {"one_group_post_survey", "stratified_post_survey"}:
        if config.survey_analysis_goal == "favorable_proportion":
            for multiplier in (0.8, 1.0, 1.2):
                variant = config_from_dict(config_to_dict(config))
                variant.survey_margin_of_error = max(config.survey_margin_of_error * multiplier, 1e-9)
                variants.append((f"margin x {multiplier:.1f}", variant))
            for expected in (0.50, config.survey_expected_proportion):
                variant = config_from_dict(config_to_dict(config))
                variant.survey_expected_proportion = expected
                variants.append((f"expected favorable {expected:.0%}", variant))
        else:
            for multiplier in (0.8, 1.0, 1.2):
                variant = config_from_dict(config_to_dict(config))
                variant.survey_mean_margin_of_error = max(config.survey_mean_margin_of_error * multiplier, 1e-9)
                variants.append((f"mean margin x {multiplier:.1f}", variant))
            if config.survey_expected_sd is not None:
                for multiplier in (0.8, 1.2):
                    variant = config_from_dict(config_to_dict(config))
                    variant.survey_expected_sd = max(config.survey_expected_sd * multiplier, 1e-9)
                    variants.append((f"SD x {multiplier:.1f}", variant))
    elif config.outcome_type == "continuous":
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
    if config.study_design == "stratified_post_survey":
        return "Stratified post-intervention survey confidence interval"
    if config.study_design == "one_group_post_survey":
        return "One-group post-intervention survey confidence interval"
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
        "one_group_post_survey": "One-group post-intervention survey",
        "stratified_post_survey": "Stratified post-intervention survey",
    }
    return mapping[config.study_design]


def _group_text(config: StudyConfig, groups: GroupSizes) -> str:
    if config.study_design in {"one_group_pre_post", "one_group_post_survey", "stratified_post_survey"}:
        return f"{groups.intervention} participants"
    return (
        f"{groups.control} {config.control_label} + "
        f"{groups.intervention} {config.intervention_label} = {groups.total}"
    )


def _target_text_en(config: StudyConfig, target: EvaluationTarget) -> str:
    status = "reached" if target.achieved else f"needs {target.additional_total} more valid participants"
    if config.study_design in {"one_group_pre_post", "one_group_post_survey", "stratified_post_survey"}:
        return f"- {target.label}: requires {target.required_total} valid participants; {status}."
    return (
        f"- {target.label}: requires {target.required_control} {config.control_label} and "
        f"{target.required_intervention} {config.intervention_label}; {status}."
    )


def _target_text_pt(config: StudyConfig, target: EvaluationTarget) -> str:
    status = "alcancado" if target.achieved else f"faltam {target.additional_total} participantes validos"
    if config.study_design in {"one_group_pre_post", "one_group_post_survey", "stratified_post_survey"}:
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
        f"Analysis unit: {c.analysis_unit}",
        f"Observation unit: {c.observation_unit}",
    ]
    if c.analysis_mode == "plan" and c.study_design in {"one_group_post_survey", "stratified_post_survey"}:
        goal = (
            f"favorable proportion >= {c.survey_target_proportion:.1%} with margin about {c.survey_margin_of_error:.1%}"
            if c.survey_analysis_goal == "favorable_proportion"
            else f"mean score with margin about {c.survey_mean_margin_of_error:.3f}"
        )
        lines.extend(
            [
                "",
                "Planning result",
                f"- Initial valid survey target: {_group_text(c, plan.initial_valid)}.",
                f"- Design-adjusted valid target: {_group_text(c, plan.design_adjusted_valid)}.",
                f"- To assign or start: {_group_text(c, plan.assigned_needed)}.",
                f"- To invite or contact: {_group_text(c, plan.invited_needed)}.",
                f"- Confidence level: {(1 - plan.alpha_adjusted):.1%}; goal: {goal}.",
                f"- Scale: {c.survey_scale_min:g} to {c.survey_scale_max:g}; favorable responses are >= {c.survey_favorable_threshold:g}.",
                f"- Design effect: {plan.design_effect:.3f}; effective data rate: {plan.effective_data_rate:.1%}.",
            ]
        )
        if plan.stratified_survey_analysis:
            lines.extend(_stratified_report_lines_en(plan.stratified_survey_analysis))
    elif c.analysis_mode == "plan":
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
            ]
        )
        if obs.survey_analysis:
            lines.extend(_survey_report_lines_en(obs.survey_analysis))
            if plan.stratified_survey_analysis:
                lines.extend(_stratified_report_lines_en(plan.stratified_survey_analysis))
        elif obs.observed_effect_size is None:
            lines.extend(
                [
                    "- No observed effect was entered; p-value and achieved power are not unique.",
                    "- Use the sample-capacity table below to see minimum detectable effects for common standards.",
                ]
            )
        else:
            assert obs.z_statistic is not None
            assert obs.p_value is not None
            assert obs.achieved_power is not None
            lines.extend(
                [
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
        if obs.capacity_rows:
            lines.extend(["", "Sample-size capacity"])
            lines.extend(
                f"- {row.label}: {row.effect_label}; observed sample {row.total} valid participants."
                if row.effect_size is not None
                else f"- {row.label}: effect is outside the feasible range for this sample."
                for row in obs.capacity_rows
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
    if c.notes.strip():
        lines.extend(["", "Notes", c.notes.strip()])
    return "\n".join(lines)


def _survey_report_lines_en(survey: SurveyAnalysis) -> list[str]:
    lines = [
        f"- Survey confidence level: {survey.confidence_level:.1%}.",
        f"- Valid responses: {survey.valid_n}; missing/NA: {survey.missing_n}.",
        "- No p-value or power is reported because this is descriptive opinion estimation.",
    ]
    if survey.favorable_proportion is not None:
        assert survey.favorable_ci_low is not None
        assert survey.favorable_ci_high is not None
        claim = "supported" if survey.target_reached else "not supported"
        lines.extend(
            [
                f"- Favorable responses: {survey.favorable_count} ({survey.favorable_proportion:.1%}).",
                f"- Favorable-response CI: {survey.favorable_ci_low:.1%} to {survey.favorable_ci_high:.1%}.",
                f"- Target claim at {survey.target_proportion:.1%}: {claim}.",
            ]
        )
    if survey.mean is not None:
        lines.append(f"- Mean score: {survey.mean:.3f}.")
        if survey.sd is not None:
            lines.append(f"- Score SD: {survey.sd:.3f}.")
        if survey.mean_ci_low is not None and survey.mean_ci_high is not None:
            lines.append(f"- Mean-score CI: {survey.mean_ci_low:.3f} to {survey.mean_ci_high:.3f}.")
        if survey.target_mean is not None and survey.target_mean_reached is not None:
            claim = "supported" if survey.target_mean_reached else "not supported"
            lines.append(f"- Target mean at {survey.target_mean:.3f}: {claim}.")
    if survey.margin_of_error is not None:
        formatted = f"{survey.margin_of_error:.1%}" if survey.favorable_proportion is not None else f"{survey.margin_of_error:.3f}"
        lines.append(f"- Approximate margin of error: {formatted}.")
    if survey.category_rows:
        lines.append("")
        lines.append("Survey response distribution")
        for row in survey.category_rows:
            marker = " favorable" if row.favorable else ""
            if row.missing:
                marker = " missing/NA"
            bar = "#" * min(40, round(row.proportion * 40))
            lines.append(
                f"- {row.label}: {row.count} ({row.proportion:.1%}; CI {row.ci_low:.1%} to {row.ci_high:.1%}){marker} {bar}"
            )
    return lines


def _stratified_report_lines_en(analysis: StratifiedSurveyAnalysis) -> list[str]:
    lines = [
        "",
        "Stratified representation",
        f"- Allocation method: {analysis.allocation_method.replace('_', ' ')}.",
        f"- Planned valid total by strata: {analysis.target_total_valid}.",
        f"- Planned assigned/starters by strata: {analysis.assigned_total}; invited/contacted: {analysis.invited_total}.",
        f"- Use weights: {'yes' if analysis.use_weights else 'no'}; effective data rate: {analysis.effective_data_rate:.1%}.",
    ]
    if analysis.plan_rows:
        lines.append("- Planned strata:")
        for row in analysis.plan_rows:
            weight = f"; weight {row.weight:.3f}" if row.weight is not None else ""
            lines.append(
                f"  - {row.label}: population share {row.population_proportion:.1%}; "
                f"target {row.target_valid_n}; assign {row.assigned_needed}; invite {row.invited_needed}{weight}."
            )
    if analysis.observed_rows:
        lines.append("- Observed strata:")
        for row in analysis.observed_rows:
            share = f"{row.observed_share:.1%}" if row.observed_share is not None else "not observed"
            ratio = f"{row.representation_ratio:.2f}" if row.representation_ratio is not None else "n/a"
            fav = f"; favorable {row.favorable_proportion:.1%}" if row.favorable_proportion is not None else ""
            weight = f"; weight {row.weight:.3f}" if row.weight is not None else ""
            lines.append(
                f"  - {row.label}: expected {row.expected_proportion:.1%}; observed {row.observed_valid_n} "
                f"valid ({share}); representation ratio {ratio}; {row.status}{fav}{weight}."
            )
    return lines


def _survey_report_lines_pt(survey: SurveyAnalysis) -> list[str]:
    lines = [
        f"- Nivel de confianca do questionario: {survey.confidence_level:.1%}.",
        f"- Respostas validas: {survey.valid_n}; ausentes/NA: {survey.missing_n}.",
        "- Nao ha valor-p nem poder porque esta e uma estimativa descritiva de opiniao.",
    ]
    if survey.favorable_proportion is not None:
        assert survey.favorable_ci_low is not None
        assert survey.favorable_ci_high is not None
        claim = "sustentada" if survey.target_reached else "nao sustentada"
        lines.extend(
            [
                f"- Respostas favoraveis: {survey.favorable_count} ({survey.favorable_proportion:.1%}).",
                f"- IC das respostas favoraveis: {survey.favorable_ci_low:.1%} a {survey.favorable_ci_high:.1%}.",
                f"- Declaracao-alvo em {survey.target_proportion:.1%}: {claim}.",
            ]
        )
    if survey.mean is not None:
        lines.append(f"- Media da escala: {survey.mean:.3f}.")
        if survey.sd is not None:
            lines.append(f"- DP da escala: {survey.sd:.3f}.")
        if survey.mean_ci_low is not None and survey.mean_ci_high is not None:
            lines.append(f"- IC da media: {survey.mean_ci_low:.3f} a {survey.mean_ci_high:.3f}.")
        if survey.target_mean is not None and survey.target_mean_reached is not None:
            claim = "sustentada" if survey.target_mean_reached else "nao sustentada"
            lines.append(f"- Media-alvo em {survey.target_mean:.3f}: {claim}.")
    if survey.margin_of_error is not None:
        formatted = f"{survey.margin_of_error:.1%}" if survey.favorable_proportion is not None else f"{survey.margin_of_error:.3f}"
        lines.append(f"- Margem de erro aproximada: {formatted}.")
    if survey.category_rows:
        lines.append("")
        lines.append("Distribuicao das respostas do questionario")
        for row in survey.category_rows:
            marker = " favoravel" if row.favorable else ""
            if row.missing:
                marker = " ausente/NA"
            bar = "#" * min(40, round(row.proportion * 40))
            lines.append(
                f"- {row.label}: {row.count} ({row.proportion:.1%}; IC {row.ci_low:.1%} a {row.ci_high:.1%}){marker} {bar}"
            )
    return lines


def _stratified_report_lines_pt(analysis: StratifiedSurveyAnalysis) -> list[str]:
    lines = [
        "",
        "Representacao estratificada",
        f"- Metodo de alocacao: {analysis.allocation_method.replace('_', ' ')}.",
        f"- Total valido planejado por estratos: {analysis.target_total_valid}.",
        f"- Participantes planejados para iniciar por estratos: {analysis.assigned_total}; convidados/contatados: {analysis.invited_total}.",
        f"- Usar pesos: {'sim' if analysis.use_weights else 'nao'}; taxa efetiva de dados: {analysis.effective_data_rate:.1%}.",
    ]
    if analysis.plan_rows:
        lines.append("- Estratos planejados:")
        for row in analysis.plan_rows:
            weight = f"; peso {row.weight:.3f}" if row.weight is not None else ""
            lines.append(
                f"  - {row.label}: participacao populacional {row.population_proportion:.1%}; "
                f"alvo {row.target_valid_n}; iniciar {row.assigned_needed}; convidar {row.invited_needed}{weight}."
            )
    if analysis.observed_rows:
        lines.append("- Estratos observados:")
        for row in analysis.observed_rows:
            share = f"{row.observed_share:.1%}" if row.observed_share is not None else "nao observado"
            ratio = f"{row.representation_ratio:.2f}" if row.representation_ratio is not None else "n/a"
            fav = f"; favoravel {row.favorable_proportion:.1%}" if row.favorable_proportion is not None else ""
            weight = f"; peso {row.weight:.3f}" if row.weight is not None else ""
            lines.append(
                f"  - {row.label}: esperado {row.expected_proportion:.1%}; observado {row.observed_valid_n} "
                f"validos ({share}); razao de representacao {ratio}; {row.status}{fav}{weight}."
            )
    return lines


def _render_pt(plan: SamplePlan) -> str:
    c = plan.config
    path_map = {
        "parallel_two_group": "Dois grupos independentes",
        "pretest_posttest_control": "Pré-teste/pós-teste com controle",
        "one_group_pre_post": "Pré-teste/pós-teste com um grupo",
        "one_group_post_survey": "Questionario pos-intervencao com um grupo",
        "stratified_post_survey": "Questionario pos-intervencao estratificado",
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
        f"Unidade de analise: {c.analysis_unit}",
        f"Unidade de observacao: {c.observation_unit}",
    ]
    if c.analysis_mode == "plan" and c.study_design in {"one_group_post_survey", "stratified_post_survey"}:
        goal = (
            f"proporcao favoravel >= {c.survey_target_proportion:.1%} com margem perto de {c.survey_margin_of_error:.1%}"
            if c.survey_analysis_goal == "favorable_proportion"
            else f"media da escala com margem perto de {c.survey_mean_margin_of_error:.3f}"
        )
        lines.extend(
            [
                "",
                "Resultado do planejamento",
                f"- Alvo inicial valido do questionario: {_group_text(c, plan.initial_valid)}.",
                f"- Alvo valido apos correcoes de desenho: {_group_text(c, plan.design_adjusted_valid)}.",
                f"- Participantes para iniciar/alocar: {_group_text(c, plan.assigned_needed)}.",
                f"- Pessoas para convidar/contatar: {_group_text(c, plan.invited_needed)}.",
                f"- Nivel de confianca: {(1 - plan.alpha_adjusted):.1%}; objetivo: {goal}.",
                f"- Escala: {c.survey_scale_min:g} a {c.survey_scale_max:g}; respostas favoraveis sao >= {c.survey_favorable_threshold:g}.",
                f"- Efeito de desenho: {plan.design_effect:.3f}; taxa efetiva de dados: {plan.effective_data_rate:.1%}.",
            ]
        )
        if plan.stratified_survey_analysis:
            lines.extend(_stratified_report_lines_pt(plan.stratified_survey_analysis))
    elif c.analysis_mode == "plan":
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
            ]
        )
        if obs.survey_analysis:
            lines.extend(_survey_report_lines_pt(obs.survey_analysis))
            if plan.stratified_survey_analysis:
                lines.extend(_stratified_report_lines_pt(plan.stratified_survey_analysis))
        elif obs.observed_effect_size is None:
            lines.extend(
                [
                    "- Nenhum efeito observado foi informado; valor-p e poder alcançado não são únicos.",
                    "- Use a tabela de capacidade da amostra abaixo para ver efeitos mínimos detectáveis para padrões comuns.",
                ]
            )
        else:
            assert obs.z_statistic is not None
            assert obs.p_value is not None
            assert obs.achieved_power is not None
            lines.extend(
                [
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
        if obs.capacity_rows:
            lines.extend(["", "Capacidade da amostra"])
            lines.extend(
                f"- {row.label}: {row.effect_label}; amostra observada {row.total} participantes validos."
                if row.effect_size is not None
                else f"- {row.label}: efeito fora da faixa viavel para esta amostra."
                for row in obs.capacity_rows
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
    if c.notes.strip():
        lines.extend(["", "Notas", c.notes.strip()])
    return "\n".join(lines)
