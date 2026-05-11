# Intervention Sample Planner

<!-- File version: 1.0; date: 2026-05-11 -->

Intervention Sample Planner is a local desktop app for planning the sample size of a two-group intervention study.

Current application version: **ISP v1.0**.

Documentation policy: the English Markdown files are the canonical originals. Files ending in `_pt.md` are Portuguese translations of those English originals.

It is designed for experiments where one group receives an intervention and another group does not, such as:

- an educational game versus a standard lesson;
- a new tutorial versus the current tutorial;
- an adaptive feedback version versus a fixed feedback version;
- a health, training, usability, or learning intervention versus a control condition.

The app does not only answer "how many people?". It separates the methodological stages that researchers often mix together:

1. How many valid analyzable cases are needed if everyone provides data?
2. How should those cases be divided between intervention and control?
3. How much does the target change when the population is finite, data are clustered, or alpha is adjusted for multiple planned comparisons?
4. How many people must be assigned, recruited, or invited after dropout, nonresponse, and invalid data are considered?
5. How should the sample-size decision be explained in a paper, TCC, dissertation, thesis, protocol, or ethics submission?

## Main Features

- Local Tkinter app, no web server required.
- Pure Python calculation API for reuse in scripts, notebooks, tests, or future interfaces.
- Wizard mode with explanations for each question.
- Direct configuration mode with every variable shown in one place.
- A `?` help button beside each field.
- English and Portuguese interface/report support.
- Results tabs for summary, sensitivity, and JSON.
- Formatted sensitivity table.
- Save and load study configurations as JSON.
- Export the planning report as text.
- Source-based example cases and unit tests.

## What It Calculates

Current version:

- Two independent means using Cohen's `d`.
- Two independent proportions, such as completion, success, error, dropout, or return rate.
- Equal or unequal allocation between intervention and control.
- Two-sided or one-sided planning.
- Bonferroni alpha adjustment for multiple planned primary comparisons.
- Optional finite-population correction.
- Optional cluster design effect: `DEFF = 1 + (m - 1) * ICC`.
- Response/start rate, completion rate, usable-data rate, and extra buffer.
- Sensitivity scenarios for smaller/larger effect values and stronger target power.

The calculations use normal approximations. Exact tools such as G*Power or R `pwr` can sometimes return one additional participant per group because they use t-distribution or iterative exact methods.

## Run the App

From the repository folder:

```powershell
cd D:\GitHub\InterventionSamplePlanner
python run_app.py
```

or:

```powershell
python -m intervention_sample_planner
```

If you are using the generated Windows executable, open:

```text
dist\InterventionSamplePlanner\InterventionSamplePlanner.exe
```

or, if built as one file:

```text
dist\InterventionSamplePlanner.exe
```

## Quick Test Problems

Use these cases to check whether the app is behaving as expected.

### 1. Mean Difference, Teaching Intervention

Problem: a new teaching method is compared with a standard lecture. The researcher wants 80% power to detect a medium standardized mean difference.

Inputs:

- outcome type: continuous;
- Cohen's d: `0.5`;
- alpha: `0.05`;
- power: `0.80`;
- allocation ratio: `1`;
- response, completion, usable data: `1`.

Expected app result:

- valid control: `63`;
- valid intervention: `63`;
- valid total: `126`.

This matches the normal-approximation worked example in StatsIQ. Exact software may report `64` per group.

### 2. Mean Difference With 15% Dropout

Same case as above, but completion rate is `0.85`.

Expected app result:

- initial valid target: `63 + 63 = 126`;
- participants to assign/start: `75 + 75 = 150`.

Why: `63 / 0.85 = 74.12`, rounded up to `75` per group.

### 3. Binary Outcome, Completion Rate

Problem: a game version with adaptive support should raise level completion from 45% to 60%.

Inputs:

- outcome type: binary;
- control proportion: `0.45`;
- intervention proportion: `0.60`;
- alpha: `0.05`;
- power: `0.80`;
- allocation ratio: `1`.

Expected app result:

- valid control: `173`;
- valid intervention: `173`;
- valid total: `346`.

### 4. Clustered Classrooms

Problem: students are nested in classes, and students in the same class are more similar than independent students.

Inputs:

- use the continuous `d = 0.5` case;
- average cluster size: `25`;
- ICC: `0.05`.

Expected app result:

- design effect: `2.2`;
- corrected valid control: `139`;
- corrected valid intervention: `139`;
- corrected valid total: `278`.

## Loading Examples

Example JSON files are included in:

```text
examples\
examples\from_sources\
```

Use `examples\` for simple app configurations and `examples\from_sources\` for documented cases that include source metadata and expected outputs.

In the app:

1. Open **Data / Configuration**.
2. Click **Load config**.
3. Choose one of the JSON files.
4. Click **Calculate**.
5. Check the **Results** tabs.

The `examples/from_sources` files also include a `source_case` block with source URL, real-world problem, and expected calculator outputs. The app ignores those metadata fields, but the test suite uses them.

## JSON Schema

Configuration files can be documented and checked with JSON Schema:

```text
schemas/study_config.schema.json
```

The example JSON files include a `$schema` field that points to this schema. Editors such as VS Code can use it for autocomplete, field descriptions, and basic validation. The app itself is permissive: it ignores unknown metadata fields such as `$schema`, `_file_version`, `_file_date`, and `source_case` when loading a configuration.

The schema describes the current `StudyConfig` fields, supported values, numeric ranges, and conditional rules such as requiring `finite_population` when `apply_fpc` is true.

## Run Tests

```powershell
cd D:\GitHub\InterventionSamplePlanner
python -m unittest discover -s tests
```

The tests verify:

- the examples from `resumoteoria.md`;
- the source-based example JSON files;
- dropout correction;
- cluster design-effect correction;
- config loading that ignores metadata fields.

## API Use

```python
from intervention_sample_planner import StudyConfig, calculate_plan, render_report

config = StudyConfig(
    study_name="Educational intervention validation",
    outcome_type="continuous",
    effect_size_d=0.5,
    alpha=0.05,
    power=0.80,
    allocation_ratio=1.0,
    completion_rate=0.85,
)

plan = calculate_plan(config)
print(plan.initial_valid.total)
print(plan.assigned_needed.total)
print(render_report(plan, "en"))
```

## How to Interpret Results

The app reports several different sample numbers on purpose:

- **Initial valid data target**: the theoretical valid/analyzable sample if everyone provides usable data.
- **Corrected valid data target**: the valid sample after finite population and cluster/design corrections.
- **Participants to assign/start**: how many people should begin after completion and usable-data losses are considered.
- **People to invite/contact**: how many people to contact after the response/start rate is considered.

For example, if a study needs 63 valid participants per group and expects 15% dropout, it should not recruit only 63 per group. It should start about 75 per group to preserve the valid-data target.

## Methodological Orientation

The app follows the methodological rule summarized in [`resumoteoria.md`](resumoteoria.md): sample size is part of evidence planning, not just a formula.

The central assumptions are:

- sample size must match the inference being claimed;
- a causal or intervention claim needs comparison and control;
- power analysis requires alpha, power, effect size, variability or rates, and allocation ratio;
- the calculated sample is valid analyzable data, not invitations;
- dropout, nonresponse, invalid data, clusters, and multiple comparisons should be planned before data collection;
- conclusions should be proportional to the evidence.

External sources used as orientation:

- [StatsIQ worked example](https://www.statisticstutor.app/study-guides/statistical-power-sample-size-calculation-type-ii-error)
- [StatsMasters effect size and power lesson](https://statsmasters.com/lessons/effect-size-power/)
- [G*Power](https://www.psychologie.hhu.de/arbeitsgruppen/allgemeine-psychologie-und-arbeitspsychologie/gpower/news-page)
- [G*Power 3.1 manual](https://www.psychologie.hhu.de/fileadmin/redaktion/Fakultaeten/Mathematisch-Naturwissenschaftliche_Fakultaet/Psychologie/AAP/gpower/GPowerManual.pdf)
- [statsmodels power and sample-size documentation](https://www.statsmodels.org/stable/stats.html)
- [R pwr.t.test documentation](https://search.r-project.org/CRAN/refmans/pwr/html/pwr.t.test.html)
- [OpenEpi cohort and clinical-trial sample-size documentation](https://www.openepi.com/Documentation/SSCohortdoc.htm)
- [J-PAL sample size and power examples](https://github.com/J-PAL/Sample_Size_and_Power)

## Difference From the Orientation Sources

This app was inspired by established sample-size and power tools, but it has a different purpose. The goal is not to replace specialized statistical software. The goal is to guide a researcher through one common intervention-planning workflow and make the recruitment consequences explicit.

| Source | What it is good for | How this app is different |
| --- | --- | --- |
| G*Power and the G*Power 3.1 manual | Broad desktop power-analysis software. It supports many test families, including exact, F, t, chi-square, z, and several regression/correlation cases. It also supports a priori, compromise, criterion, post-hoc, and sensitivity analysis, effect-size calculators, distribution plots, and a protocol output. | This app is narrower: it focuses on two-group intervention planning. It adds workflow language around valid data, assignment/start targets, invitation targets, attrition, usable-data loss, finite populations, clusters, and a paper-ready justification paragraph. |
| statsmodels | Python library with reusable statistical power classes and functions. It is better for developers who want programmatic power analysis inside a larger Python workflow. | This app keeps a simple dependency-free API plus a Tkinter interface. It is easier for local planning and teaching, but much less complete than statsmodels. |
| R `pwr.t.test` | Compact R function for solving one missing parameter in t-test power planning. It is exact enough for common t-test planning and integrates naturally with R analysis scripts. | This app adds guided explanations, bilingual labels, JSON project files, recruitment corrections, and a graphical workflow. It currently uses normal approximations, so it may differ by one participant per group from exact t-based functions. |
| OpenEpi | Public-health style calculators for sample size and epidemiological designs, with inputs such as confidence, power, group ratio, and expected outcome frequency. | This app borrows that practical input style but is framed for intervention validation with a control group, dropout/nonresponse planning, and thesis/protocol writing. |
| J-PAL examples | Applied research examples for impact evaluation, including clustered and field-experiment thinking. | This app includes a simple cluster design-effect correction but does not yet implement the full range of field-experiment power models, covariate adjustment, compliance assumptions, or randomization-level designs. |
| StatsIQ and StatsMasters examples | Worked educational examples that show how alpha, power, effect size, and sample size interact. | This app turns similar examples into loadable JSON cases and tests, then extends them with correction stages for the number of people to start or invite. |

## Limits

This app is a planning companion. It does not replace a statistician for high-stakes decisions or complex designs.

Use specialized review for:

- clinical, legal, safety, or institutional decisions;
- longitudinal outcomes;
- repeated measures beyond simple two-group planning;
- mixed models;
- covariate-adjusted power;
- non-normal or rare outcomes requiring specialized models;
- stepped-wedge, crossover, adaptive, or Bayesian designs.

For the Portuguese translation, see [README_pt.md](README_pt.md). For development details, see [developers.md](developers.md). For executable builds, see [build.md](build.md).
