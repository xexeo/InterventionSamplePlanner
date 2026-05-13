<!-- File version: 2.1; date: 2026-05-12 -->

# Developer Notes

## Main architecture

`intervention_sample_planner/calculator.py`
: calculation engine, design selection, planning mode, and achieved-result mode.

`intervention_sample_planner/gui.py`
: Tkinter interface, wizard, direct configuration mode, range overrides, and suggestions tab.

`intervention_sample_planner/web_app.py`
: Flask REST API and static-file server for the browser interface.

`intervention_sample_planner/web_static/`
: plain HTML, CSS, and JavaScript browser client. It calls the REST API and does not reimplement statistical formulas.

`intervention_sample_planner/explanations.json`
: long-form explanations, recommended ranges, and design descriptions used by the GUI.

`intervention_sample_planner/content.py`
: loader helpers for `explanations.json`.

## Study paths in v2.1

- `parallel_two_group`
- `pretest_posttest_control`
- `one_group_pre_post`

Binary planning is supported in `parallel_two_group`. Achieved-result binary evaluation is supported in `parallel_two_group` and in paired one-group pre/post cases through the McNemar fields.

## Range checking

Recommended ranges are stored in `explanations.json`. The GUI checks them and blocks out-of-range values unless the user explicitly enables the override checkbox for that field. Accepted overrides are stored in `range_override_fields`.

## Inverse mode

The inverse workflow is represented by:

- `workflow_path = "evaluate_done"` for a completed study without a previous plan
- `workflow_path = "evaluate_against_plan"` for a completed study compared with a previous plan
- `analysis_mode = "evaluate"`
- `had_planned_sample`
- `planned_control_n`
- `planned_intervention_n`
- `planned_total_n`
- `planned_effect_size`
- `planned_alpha`
- `planned_power`
- `observed_control_n`
- `observed_intervention_n`
- `observed_total_n`
- `observed_control_events`
- `observed_intervention_events`
- `observed_pre_success_post_failure`
- `observed_pre_failure_post_success`
- `observed_effect_size`

The GUI can load a saved planning JSON through `load_previous_plan()`. The result object includes `observed_analysis` with approximate `z`, `p_value`, `achieved_power`, observed binary rates when available, optional `exact_p_value`, benchmark targets, and previous-plan targets.

## v2.1 statistical methods

- Two-group binary achieved-result evaluation computes Fisher's exact p-value when event counts are available and uses it as the reported p-value for small samples or sparse cells.
- One-group paired binary achieved-result evaluation uses the exact McNemar/binomial test from `observed_pre_success_post_failure` and `observed_pre_failure_post_success`.
- Pre-test/post-test with control remains an ANCOVA-style planning and evaluation approximation, not a fitted ANCOVA model.
- Cluster support remains a design-effect approximation. Future work should add explicit cluster counts, arm-level cluster allocation, and mixed-model or cluster-randomized power routines.

## Report export

`calculator.py` exposes `render_report_html()`, `save_report_html()`, and `save_report_pdf()`. The PDF writer is dependency-free and intentionally simple, suitable for release reports but not a replacement for typeset documentation.

## Web interface and REST API

The web interface is intentionally small: Flask serves the static client and exposes JSON endpoints. There is no database, no persistent server-side user storage, and no Node.js build step.

Main endpoints:

- `GET /health`
- `GET /api/version`
- `GET /api/default-config`
- `GET /api/explanations?language=en`
- `GET /api/ui-text?language=en`
- `POST /api/calculate`
- `POST /api/report/text`
- `POST /api/report/html`
- `POST /api/report/pdf`

The `POST` endpoints accept the same configuration shape described by `schemas/study_config.schema.json`. Browser save/load is done with local file upload and download.

## Build implications

If you change `explanations.json`, remember that the executable build must include it with PyInstaller `--add-data`. If you package the web interface into a distributable Python package, also include `intervention_sample_planner/web_static/*` as package data.
