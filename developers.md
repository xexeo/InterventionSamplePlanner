<!-- File version: 2.0; date: 2026-05-11 -->

# Developer Notes

## Main architecture

`intervention_sample_planner/calculator.py`
: calculation engine, design selection, planning mode, and achieved-result mode.

`intervention_sample_planner/gui.py`
: Tkinter interface, wizard, direct configuration mode, range overrides, and suggestions tab.

`intervention_sample_planner/explanations.json`
: long-form explanations, recommended ranges, and design descriptions used by the GUI.

`intervention_sample_planner/content.py`
: loader helpers for `explanations.json`.

## Study paths in v2.0

- `parallel_two_group`
- `pretest_posttest_control`
- `one_group_pre_post`

Binary outcomes are currently supported only in `parallel_two_group`.

## Range checking

Recommended ranges are stored in `explanations.json`. The GUI checks them and blocks out-of-range values unless the user explicitly enables the override checkbox for that field. Accepted overrides are stored in `range_override_fields`.

## Inverse mode

The inverse workflow is represented by:

- `analysis_mode = "evaluate"`
- `observed_control_n`
- `observed_intervention_n`
- `observed_total_n`
- `observed_effect_size`

The result object includes `observed_analysis` with approximate `z`, `p_value`, and `achieved_power`.

## Build implications

If you change `explanations.json`, remember that the executable build must include it with PyInstaller `--add-data`.
