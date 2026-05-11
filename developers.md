# Developer Guide

<!-- File version: 1.0; date: 2026-05-11 -->

This guide is for people who want to add formulas, new interfaces, translations, tests, or distribution workflows.

Documentation policy: this English file is the canonical original. `developers_pt.md` is its Portuguese translation.

## Project Structure

```text
intervention_sample_planner/
  __init__.py
  __main__.py
  calculator.py
  gui.py
  i18n.py
examples/
  from_sources/
tests/
scripts/
schemas/
run_app.py
README.md
README_pt.md
build.md
build_pt.md
developers.md
developers_pt.md
resumoteoria.md
resumoteoria_pt.md
requirements-build.txt
```

The project has two layers:

- `calculator.py`: pure calculation API, no Tkinter, no file dialogs, no GUI state.
- `gui.py`: Tkinter interface that reads/writes a `StudyConfig`, calls `calculate_plan`, and renders results.

Keep that separation. A future CLI, web UI, or notebook wrapper should be able to reuse `calculator.py` without importing Tkinter.

## Core Data Model

The main input is `StudyConfig`.

Important fields:

- `outcome_type`: `continuous` or `binary`;
- `alpha`, `power`, `alternative`;
- `allocation_ratio`: intervention/control;
- `effect_size_d` for continuous outcomes;
- `proportion_control` and `proportion_intervention` for binary outcomes;
- correction fields such as `finite_population`, `cluster_average_size`, `intraclass_correlation`, `response_rate`, `completion_rate`, and `usable_data_rate`.

The main output is `SamplePlan`.

Important output stages:

- `initial_valid`: target valid data assuming everyone provides usable data;
- `fpc_adjusted_valid`: after finite-population correction;
- `design_adjusted_valid`: after cluster/design correction;
- `assigned_needed`: participants to assign/start after completion and usable-data correction;
- `invited_needed`: people to invite/contact after response-rate correction;
- `sensitivity`: rows shown in the sensitivity table.

## Adding a New Calculation

Recommended workflow:

1. Add or extend `SUPPORTED_OUTCOMES` in `calculator.py`.
2. Add input fields to `StudyConfig`.
3. Add validation in `_validate_config`.
4. Implement a private calculation function, following the style of `_continuous_initial` or `_binary_initial`.
5. Route `calculate_plan` and `_calculate_no_sensitivity` to the new function.
6. Add formulas to the returned `formulas` list.
7. Add warnings when assumptions are fragile.
8. Add i18n field labels and help text in `i18n.py`.
9. Add the field to `FIELD_GROUPS` and `FIELD_TYPES` in `gui.py`.
10. Add example JSON and unit tests.

Prefer clear formulas and conservative validation over clever code. Sample-size software is trusted when its assumptions are visible.

## GUI Notes

The GUI uses standard Tkinter and `ttk`.

Key patterns:

- Every editable field should have a `field_...` label in `i18n.py`.
- Every editable field should have a `help_...` explanation in `i18n.py`.
- Wizard questions use `wizard_question_...` and `wizard_why_...`.
- Direct configuration and wizard mode share `self.vars`, so changing one mode updates the same configuration state.
- The sensitivity tab uses a `ttk.Treeview`, not a text widget.

Avoid adding heavy GUI dependencies unless there is a strong reason. The current advantage is that the app runs with a normal Python installation.

## Translations

Interface/report translations live in `i18n.py`. Documentation translations live beside their English originals using the `_pt.md` suffix.

When adding a field or user-facing concept:

1. Add English label and help text.
2. Add Portuguese label and help text.
3. Use examples in both languages when the concept is easy to misunderstand.
4. Keep technical terms consistent with the report text.
5. Update the English Markdown first, then update the matching `_pt.md` translation.

## Example Cases

Source-based examples live in:

```text
examples/from_sources/
```

Each JSON file should contain:

- normal `StudyConfig` fields;
- a `source_case` block with:
  - `source_name`;
  - `source_url` or `source_file`;
  - `real_life_problem`;
  - `calculator_expected`;
  - optional `note`.

The app ignores unknown metadata fields. The tests use them.

## JSON Schema

The configuration schema lives in:

```text
schemas/study_config.schema.json
```

Keep it aligned with `StudyConfig` in `calculator.py`. When adding a config field, update the schema properties and tests. The schema intentionally allows additional properties so example metadata and future-compatible files can still be loaded by the app.

## Tests

Run:

```powershell
python -m unittest discover -s tests
```

Tests should cover:

- known numeric examples;
- each correction layer;
- source example JSON files;
- config serialization behavior;
- any new formula before it appears in the UI.

For formulas that differ from exact software by one participant per group, document why in the example metadata and assert the calculator's own intended approximation.

## Coding Style

- Keep the calculator dependency-free unless there is a strong reason.
- Keep GUI code out of `calculator.py`.
- Use dataclasses for inputs and outputs.
- Round sample-size requirements upward with `math.ceil`.
- Add warnings for methodological traps rather than silently accepting risky inputs.
- Keep comments short and useful.
- Preserve JSON backward compatibility where practical by ignoring unknown fields.

## Roadmap Ideas

Possible next features:

- exact t-distribution power for two independent means;
- paired/pre-post designs;
- non-inferiority and equivalence designs;
- regression and covariate-adjusted power;
- finite-population descriptive survey modes;
- CSV export for the sensitivity table;
- PDF or Markdown report export;
- richer Portuguese report templates;
- icons and signed installers for Windows and macOS.
