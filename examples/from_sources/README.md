# Source-Based Example Cases

<!-- File version: 1.0; date: 2026-05-11 -->

Documentation policy: this English file is the canonical original. `README_pt.md` is its Portuguese translation.

These JSON files are meant to be loaded by the app and by the test suite.
Each file contains a normal app configuration plus a `source_case` block with
the external source or local `resumoteoria.md` source, the real-world problem,
and expected outputs for this calculator.

The calculator uses the normal-approximation formulas from the methodology
summary in `resumoteoria.md`. Some exact tools, such as G*Power or R `pwr`,
may return one more participant per group because they use t-distribution or
iterative exact procedures. The examples document that distinction when it matters.

Current source-based examples include:

- `statsiq_teaching_method_d05.json`;
- `statsmasters_medium_effect_power90.json`;
- `methodology_two_proportions_completion_45_60.json`;
- `methodology_clustered_classroom_icc.json`;
- `dropout_correction_assignment_15_percent.json`.

Each JSON file includes a `$schema` field that points to `schemas/study_config.schema.json`.
