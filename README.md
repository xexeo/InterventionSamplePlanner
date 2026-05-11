<!-- File version: 2.0; date: 2026-05-11 -->

# Intervention Sample Planner

Intervention Sample Planner, or `ISP`, is a local Python API and Tkinter desktop app for planning or evaluating intervention studies in human processes such as learning, training, usability, and workflow improvement.

Version `2.0` expands the app beyond the original two-group design. It now supports:

- `Two independent groups`
- `Pre-test/post-test with control group`
- `One-group pre-test/post-test`
- `Plan required sample`
- `Evaluate achieved result`
- three workflow choices at the start: plan a study, analyze a completed study, or compare a completed study with a previous plan
- loading a saved JSON plan into the completed-study comparison workflow
- recommended ranges with explicit override
- explanations loaded from a separate JSON file
- a suggestions tab with design advice and caution flags

## What it does

The app helps answer questions such as:

- How many valid participants are needed to compare intervention and control?
- How many people must complete both the pre-test and the post-test?
- How many people should be invited if some will not start or will not finish?
- If a study already ran, what approximate p-value and achieved power correspond to the observed result?

The current implementation is strongest for continuous outcomes. Binary outcomes are currently supported for the `Two independent groups` path.

## Typical research paths

### 1. Two independent groups

Use this when one group receives the intervention and another group does not. Example: a researcher in educational games wants to test whether using Uno plus a lesson improves children's post-test understanding of greater-than and less-than compared with lesson only.

### 2. Pre-test/post-test with control group

Use this when both groups are measured before and after. Example: one group completes a pre-test, plays Uno, receives a short lesson, and completes a post-test; the control group completes the same pre-test and post-test but receives only the lesson.

### 3. One-group pre-test/post-test

Use this when the same participants are measured before and after and there is no control group. Example: a researcher wants a first estimate of the learning effect of Uno between a pre-test and a post-test before running a controlled trial.

## Completed-study and inverse workflows

`Analyze a completed study` and `Compare completed study with plan` are the inverse workflows. Instead of asking how many participants are needed, they ask what an achieved sample and observed effect imply. They report approximate quantities such as:

- observed effect entered
- observed binary event rates when event counts are entered
- approximate z statistic
- approximate p-value
- approximate achieved power
- gaps to conventional benchmarks such as `p < 0.05`, `p < 0.10`, `power >= 80%`, and `power >= 90%`

If a previous plan exists, use `Compare completed study with plan`. You can type the planned sample manually or click `Load previous plan` and choose a saved JSON from an earlier planning run. The report then says whether the achieved valid sample reached the plan and how many valid participants were missing.

## Effect size in plain language

Effect size is the hardest input for many users, so `ISP v2.0` treats it more explicitly.

- In `Two independent groups`, the continuous effect size is the standardized difference between groups.
- In `Pre-test/post-test with control group`, it is the standardized difference in gain, or the post-test effect after baseline is accounted for.
- In `One-group pre-test/post-test`, it is the standardized mean change in the same participants.

Traditional anchor values such as `0.2`, `0.5`, and `0.8` can be useful as orientation, but the best effect size is the smallest effect that would be meaningful in the real study.

## Explanations and recommendations

The app now reads long-form variable explanations and recommended ranges from:

[explanations.json](intervention_sample_planner/explanations.json)

This JSON is intended to stay aligned with the operational manual and the educational manual.

## Run locally

```powershell
cd D:\GitHub\InterventionSamplePlanner
python -m unittest discover -s tests
python run_app.py
```

## Build the executable

See:

- [build.md](build.md)
- [developers.md](developers.md)
- [versions.md](versions.md)

## Main documentation

- [theoryintroduction.md](theoryintroduction.md)
- [manual.tex](docs/educational_manual/manual.tex)
- [useofAI.md](useofAI.md)
- [disclaimer.md](disclaimer.md)
