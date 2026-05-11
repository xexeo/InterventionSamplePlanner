# Operational Summary of Sample-Size Theory

<!-- File version: 1.0; date: 2026-05-11 -->

This file is a short operational guide for planning sample size in two-group intervention studies: one group receives the intervention and the other group does not. It is meant to help users apply the app, choose the right inputs, and write a defensible sample-size justification.

Documentation policy: this English file is the canonical original. `resumoteoria_pt.md` is its Portuguese translation.

It is not a full statistics textbook. It is a practical checklist for turning a research question into a sample-size plan.

## Central Idea

Sample size is not only a calculation. It is a decision about the strength of evidence the study needs to produce.

The useful question is not only:

```text
How many people do I need?
```

It is:

```text
What conclusion do I want to support, with what risk of error, using what data, in what population or context?
```

A sample is sufficient when it can answer the study question without claiming more than the evidence supports.

## Four Questions Before Any Formula

Before calculating, define:

1. What is the unit of inference?
   Examples: student, player, class, session, response, document, computational run.

2. What kind of result will be analyzed?
   Examples: learning mean, completion rate, error proportion, correlation, interview, log, case.

3. What effect would be large enough to matter?
   Examples: a 0.5 point gain on a scale, an increase from 45% to 60% completion, a meaningful reduction in errors.

4. How much uncertainty is acceptable?
   Examples: alpha 0.05, power 80%, margin of error 5%, documented saturation.

## When the Study Compares Two Groups

For validating an intervention, the common design is:

```text
Intervention group vs control group
```

This design should state:

- the main hypothesis;
- the primary outcome;
- the significance level, or alpha;
- the desired power;
- the smallest relevant effect size;
- the allocation ratio between groups;
- expected losses, dropout, nonresponse, and invalid data.

## Type I Error, Type II Error, and Power

Type I error means concluding that there is an effect when there is no real effect.

```text
P(Type I error) = alpha
```

Type II error means failing to detect a real relevant effect.

```text
P(Type II error) = beta
```

Power is the chance of detecting the planned effect if it really exists.

```text
power = 1 - beta
```

Common values:

| Decision | Common value |
| --- | --- |
| Alpha | 0.05 |
| Power | 0.80 |
| More rigorous alpha | 0.01 |
| More rigorous power | 0.90 or 0.95 |

These are conventions, not laws. Different choices should be justified when the practical, ethical, or scientific cost of error is different.

## Comparing Two Means

Use this when the primary outcome is a mean:

- learning score;
- engagement score;
- usability scale;
- average time;
- performance score.

The effect is Cohen's `d`:

```text
d = (intervention_mean - control_mean) / pooled_standard_deviation
```

For equal group sizes:

```text
n_per_group = 2 * (z_alpha + z_power)^2 / d^2
```

Example:

- alpha = 0.05, two-sided;
- power = 0.80;
- d = 0.5.

Approximate result:

```text
63 participants per group
126 participants total
```

Interpretation: the study is planned to detect a standardized mean difference of 0.5 between intervention and control.

## Comparing Two Proportions

Use this when the primary outcome is a rate:

- completed or did not complete;
- succeeded or failed;
- returned or did not return;
- dropped out or stayed;
- chose or did not choose an option.

Main inputs:

```text
control_proportion
intervention_proportion
alpha
power
allocation_ratio
```

Example:

- 45% complete in the control group;
- 60% complete in the intervention group;
- alpha = 0.05, two-sided;
- power = 0.80.

Approximate result:

```text
173 participants per group
346 participants total
```

Interpretation: comparing proportions often requires larger samples than researchers expect, especially when the expected difference is moderate.

## Unequal Groups

If group sizes are unequal, define the ratio:

```text
k = intervention_n / control_n
```

Example:

```text
k = 2
```

means the intervention group is planned to be twice as large as the control group.

Unequal groups may be necessary because of access or logistics, but they usually increase the total sample needed for the same statistical strength.

## Initial Sample, Valid Sample, and Invitations

The number produced by the main formula is usually the number of valid analyzable cases, not the number of invitations.

Separate these stages:

| Stage | Meaning |
| --- | --- |
| Initial valid target | Required analyzable cases if everyone provides usable data |
| Corrected valid target | Valid cases after finite-population, cluster, or multiple-comparison correction |
| Participants to start | People who should begin after dropout and invalid-data losses are considered |
| People to invite/contact | People who should be contacted after the response/start rate is considered |

Simple loss correction:

```text
recruited_n = required_n / (1 - loss_rate)
```

Example:

```text
63 / 0.85 = 74.12
```

Round up:

```text
75 participants per group
```

## Response Rate and Invalid Data

When not everyone invited participates:

```text
invitations = valid_n / response_rate
```

When some completed data are invalid:

```text
effective_rate = response_rate * completion_rate * usable_data_rate
```

Then:

```text
invitations = valid_n / effective_rate
```

Example:

- 292 valid responses needed;
- response rate = 40%;
- invalid or incomplete response loss = 10%.

Effective rate:

```text
0.40 * 0.90 = 0.36
```

Invitations:

```text
292 / 0.36 = 812 invitations
```

## Finite Population

Use finite-population correction only when the conclusion is restricted to a small known population.

Examples:

- all students in one course;
- all participants in one workshop;
- all players in a closed test.

Formula:

```text
n = (N * n0) / (N + n0 - 1)
```

Where:

- `N` is the finite population size;
- `n0` is the sample without correction;
- `n` is the corrected sample.

Do not use this correction when the intended conclusion is about a broad population.

## Classes, Groups, and Clusters

When participants are grouped, they are not fully independent.

Examples:

- students inside the same class;
- players inside the same team;
- participants inside the same workshop;
- patients inside the same service.

Design-effect correction:

```text
DEFF = 1 + (m - 1) * ICC
```

Where:

- `m` is the average cluster size;
- `ICC` is the intraclass correlation.

Adjusted sample:

```text
adjusted_n = independent_n * DEFF
```

Example:

- independent sample = 126;
- average class size = 25;
- ICC = 0.05.

```text
DEFF = 1 + 24 * 0.05 = 2.2
126 * 2.2 = 278
```

Result:

```text
278 students
```

## Multiple Comparisons

If the study tests several primary outcomes, the false-positive risk increases.

A simple correction is Bonferroni:

```text
adjusted_alpha = alpha / number_of_comparisons
```

Example:

```text
0.05 / 5 = 0.01
```

This reduces false positives but increases the required sample. Define in advance which comparisons are primary and which are exploratory.

## Small Studies

A small sample is not automatically a bad sample.

It can be appropriate when the goal is:

- pilot testing;
- instrument testing;
- formative evaluation;
- problem diagnosis;
- prototype refinement;
- in-depth interview;
- case study;
- hypothesis generation.

It is insufficient when the text promises:

- general effectiveness;
- definitive superiority;
- population impact;
- conclusive validation;
- absence of rare problems;
- broad generalization without a compatible design.

## If the Available Sample Is Small

Reformulate the question so it matches the evidence you can actually collect.

Avoid:

```text
The intervention improves student learning.
```

Prefer, when the design is small or exploratory:

```text
In this observed context, the intervention produced preliminary indications of improvement and identified conditions for a future evaluation with greater statistical power.
```

This does not weaken the study. It makes the conclusion proportional to the evidence.

## Planning Checklist

Before data collection:

- Did I define the population or context?
- Did I define the unit of analysis?
- Did I define the unit of observation?
- Did I choose the primary outcome?
- Did I decide whether the outcome is a mean or a proportion?
- Did I justify the relevant effect size?
- Did I choose alpha and power?
- Did I decide whether the test is two-sided or one-sided?
- Did I define the intervention/control allocation ratio?
- Did I consider losses, dropout, and invalid data?
- Did I consider response rate?
- Did I consider finite population, if applicable?
- Did I consider clusters, if applicable?
- Did I consider multiple comparisons?
- Did I write the real limit of the conclusion?

## How to Write the Sample-Size Justification

Template for two means:

```text
The experiment compared two independent groups: intervention and control. The sample size was planned to detect a standardized mean difference of d = [value] in the primary outcome, with alpha = [value], a [two-sided/one-sided] test, and power of [value]. The planned allocation ratio was [ratio]. The calculation indicated [n] valid participants per group. Considering [rate] of losses, dropout, or invalid data, the study should start approximately [corrected_n] participants per group. Conclusions will be limited to the population, context, and measure defined in the design.
```

Template for two proportions:

```text
The experiment compared the proportion of [event] between the intervention group and the control group. Planning assumed an expected proportion of [control_p] in the control group and [intervention_p] in the intervention group, with alpha = [value], a [two-sided/one-sided] test, and power of [value]. The calculation indicated [n] valid participants per group. After corrections for response, completion, and usable data, the study should invite approximately [invitations] people. Results will be interpreted in proportion to the design and observed losses.
```

Template for a small or formative study:

```text
Given restrictions in time, access, and intervention maturity, this study was planned as an exploratory and formative evaluation. The goal is not to estimate a definitive population effect, but to identify indications, usability issues, comprehension, acceptability, and conditions for a later evaluation. Quantitative results will be treated descriptively, and qualitative data will be used to interpret the observed patterns.
```

## Final Rule

Every study should collect enough evidence to answer the question it asks.

And every study should ask a question that can be answered by the evidence it can collect.
