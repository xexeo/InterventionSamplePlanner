"""Flask web interface and REST API for Intervention Sample Planner."""

# File version: 2.4; date: 2026-05-30

from __future__ import annotations

from dataclasses import asdict
from io import BytesIO
import tempfile
from pathlib import Path

from flask import Flask, jsonify, request, send_file, send_from_directory

from .calculator import (
    PlanningError,
    StudyConfig,
    calculate_plan,
    config_from_dict,
    config_to_dict,
    render_report,
    render_report_html,
    save_report_pdf,
)
from .content import load_content
from .i18n import TEXT
from .version import APP_VERSION, APP_VERSION_DATE, APP_WINDOW_TITLE


STATIC_DIR = Path(__file__).with_name("web_static")


app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")


@app.get("/")
@app.get("/app")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "version": APP_VERSION, "date": APP_VERSION_DATE})


@app.get("/api/version")
def api_version():
    return jsonify(
        {
            "version": APP_VERSION,
            "date": APP_VERSION_DATE,
            "title": APP_WINDOW_TITLE,
        }
    )


@app.get("/api/default-config")
def api_default_config():
    language = request.args.get("language", "en")
    return jsonify(config_to_dict(StudyConfig(language=language if language in {"en", "pt"} else "en")))


@app.get("/api/explanations")
def api_explanations():
    language = request.args.get("language", "en")
    content = load_content()
    return jsonify(content.get(language, content["en"]))


@app.get("/api/ui-text")
def api_ui_text():
    language = request.args.get("language", "en")
    return jsonify(TEXT.get(language, TEXT["en"]))


@app.post("/api/calculate")
def api_calculate():
    config = _config_from_request()
    plan = calculate_plan(config)
    return jsonify(_plan_payload(plan))


@app.post("/api/report/text")
def api_report_text():
    config = _config_from_request()
    plan = calculate_plan(config)
    payload = render_report(plan, config.language).encode("utf-8")
    return send_file(
        BytesIO(payload),
        mimetype="text/plain; charset=utf-8",
        as_attachment=True,
        download_name=_download_name(config.study_name, "txt"),
    )


@app.post("/api/report/html")
def api_report_html():
    config = _config_from_request()
    plan = calculate_plan(config)
    payload = render_report_html(plan, config.language).encode("utf-8")
    return send_file(
        BytesIO(payload),
        mimetype="text/html; charset=utf-8",
        as_attachment=True,
        download_name=_download_name(config.study_name, "html"),
    )


@app.post("/api/report/pdf")
def api_report_pdf():
    config = _config_from_request()
    plan = calculate_plan(config)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        path = Path(tmp.name)
    try:
        save_report_pdf(plan, path, config.language)
        payload = path.read_bytes()
    finally:
        path.unlink(missing_ok=True)
    return send_file(
        BytesIO(payload),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=_download_name(config.study_name, "pdf"),
    )


@app.errorhandler(PlanningError)
def planning_error(error: PlanningError):
    return jsonify({"error": str(error), "type": "PlanningError"}), 400


@app.errorhandler(ValueError)
def value_error(error: ValueError):
    return jsonify({"error": str(error), "type": "ValueError"}), 400


def _config_from_request() -> StudyConfig:
    data = request.get_json(force=True, silent=False)
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object.")
    return config_from_dict(data)


def _plan_payload(plan) -> dict:
    observed = asdict(plan.observed_analysis) if plan.observed_analysis else None
    stratified = asdict(plan.stratified_survey_analysis) if plan.stratified_survey_analysis else None
    return {
        "version": APP_VERSION,
        "config": config_to_dict(plan.config),
        "report": render_report(plan, plan.config.language),
        "summary": {
            "method": plan.method,
            "alpha_adjusted": plan.alpha_adjusted,
            "effect_size_used": plan.effect_size_used,
            "design_effect": plan.design_effect,
            "effective_data_rate": plan.effective_data_rate,
            "initial_valid": _group_payload(plan.initial_valid),
            "fpc_adjusted_valid": _group_payload(plan.fpc_adjusted_valid),
            "design_adjusted_valid": _group_payload(plan.design_adjusted_valid),
            "assigned_needed": _group_payload(plan.assigned_needed),
            "invited_needed": _group_payload(plan.invited_needed),
            "achieved_power_at_valid_target": plan.achieved_power_at_valid_target,
        },
        "warnings": plan.warnings,
        "suggestions": plan.suggestions,
        "formulas": plan.formulas,
        "sensitivity": [asdict(row) for row in plan.sensitivity],
        "observed_analysis": observed,
        "stratified_survey_analysis": stratified,
    }


def _group_payload(group) -> dict:
    return {
        "control": group.control,
        "intervention": group.intervention,
        "total": group.total,
    }


def _download_name(study_name: str, extension: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in study_name.strip().lower())
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return f"{cleaned or 'isp-report'}.{extension}"


def main() -> None:
    """Run the local Flask development server."""

    app.run(debug=True)


if __name__ == "__main__":
    main()
