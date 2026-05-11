# Intervention Sample Planner

Local Python app for planning the sample size of a two-group experiment that validates an intervention: one group receives the intervention and one group does not.

The project has two layers:

- API layer: `intervention_sample_planner.calculator` does the calculations without any GUI dependency.
- Interface layer: `intervention_sample_planner.gui` provides a local Tkinter app with a guided wizard and a direct configuration mode.

The app is bilingual: English (`en`) and Portuguese (`pt`).

## Why This Tool Exists

The methodology rule used here is that sample size is an evidence decision, not just a number. The app therefore separates:

1. Initial valid/analyzable group division, assuming everyone provides data.
2. Corrections for finite population, clusters/classes, and multiple primary comparisons.
3. Corrections for people who do not start, complete, or provide usable data.
4. A justification paragraph that can be adapted for a paper, TCC, dissertation, or thesis.

## What It Calculates

Current first version:

- Two independent means, using Cohen's `d`.
- Two independent proportions, such as completion, success, error, dropout, or return rate.
- Equal or unequal allocation between intervention and control.
- Two-sided or one-sided alternatives.
- Bonferroni alpha adjustment for multiple planned primary comparisons.
- Optional finite-population correction.
- Optional cluster design effect: `DEFF = 1 + (m - 1) * ICC`.
- Response/start rate, completion rate, usable-data rate, and extra buffer.
- Sensitivity table for effect size/difference and target power.

## Run Locally

From this repository:

```powershell
python run_app.py
```

or:

```powershell
python -m intervention_sample_planner
```

No external packages are required for the calculator or the Tkinter interface.

## API Example

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

## Interface Modes

Wizard mode asks questions one by one. Each question includes a short explanation of why the answer matters.

Data / Configuration mode shows all variables directly. Every variable has a `?` help button beside it, including variables used by the wizard.

Results mode has tabs for the summary, sensitivity table, and full JSON output.

## Methodological Orientation

The app follows the logic in `amostra.tex`, especially:

- sample size must match the inference being claimed;
- comparisons between two groups need power, alpha, effect size, and allocation ratio;
- the initial calculated sample is valid/analyzable data, not invitations;
- dropout, nonresponse, and invalid data must be planned explicitly;
- cluster samples need design-effect correction;
- conclusions should be proportional to the evidence.

External tools and documentation used as orientation:

- [G*Power](https://www.psychologie.hhu.de/arbeitsgruppen/allgemeine-psychologie-und-arbeitspsychologie/gpower/news-page), a local power-analysis tool for many statistical test families and plots.
- [statsmodels power and sample-size documentation](https://www.statsmodels.org/stable/stats.html), which exposes Python APIs for t, z, F, chi-square, and proportion-related power calculations.
- [R `pwr.t.test`](https://search.r-project.org/CRAN/refmans/pwr/html/pwr.t.test.html), which solves for one missing power parameter in t-test planning.
- [OpenEpi clinical/cohort sample-size documentation](https://www.openepi.com/Documentation/SSCohortdoc.htm), which emphasizes confidence level, power, group ratio, and expected group outcomes.
- [J-PAL sample size and power examples](https://github.com/J-PAL/Sample_Size_and_Power), which include applied power code for individual and clustered designs.

## Tests

Run:

```powershell
python -m unittest discover -s tests
```

The tests check the main examples from the methodology chapter:

- continuous two-group comparison with `d = 0.5`, alpha `0.05`, power `0.80`: 63 per group;
- 15% loss after assignment: 75 per group to start/assign;
- binary proportions 45% versus 60%: 173 per group;
- cluster design effect with class size 25 and ICC 0.05.

## Caution

These calculations are planning approximations. They do not replace a statistician for high-stakes clinical, legal, financial, or institutional decisions. For complex designs, mixed models, covariates, longitudinal outcomes, repeated measures, or non-normal outcomes, use this app as a planning companion and verify the design with specialized software.
