<!-- File version: 2.0; date: 2026-05-11 -->

# Operational Theory Summary for ISP v2.0

This operational manual explains how to use `ISP v2.0` in a practical way. It is shorter than the educational LaTeX manual, but it is written to support real decisions in the app.

## 1. What changed in v2.0

`ISP v1.0` focused on one design: two independent groups. `ISP v2.0` adds:

- `Two independent groups`
- `Pre-test/post-test with control group`
- `One-group pre-test/post-test`
- `Plan required sample`
- `Evaluate achieved result`
- recommended ranges with explicit override
- explanations in `intervention_sample_planner/explanations.json`
- a dedicated `Suggestions` tab

## 2. Start by choosing the research path

The first decision in the wizard is no longer the outcome type. It is the research path.

### Path A. Two independent groups

Use this when different people belong to intervention and control, and the main claim is about a difference between groups.

Educational-games example:
A researcher in educational games wants to verify whether using the game Uno helps children understand the concepts of greater-than and less-than. One group plays Uno with guided prompts and then receives a short lesson. Another group receives only the lesson. Both groups complete a final test, and the main comparison is between the groups.

### Path B. Pre-test/post-test with control group

Use this when both groups are measured before and after.

Educational-games example:
A researcher wants to examine whether Uno changes mathematical comparison concepts beyond ordinary instruction. Children in both groups complete a pre-test. The intervention group then plays Uno and receives a short lesson. The control group receives only the lesson. Both groups complete the same post-test. In this path, the pre-test helps control baseline differences and improve precision.

### Path C. One-group pre-test/post-test

Use this when there is no control group and the same participants are measured before and after.

Educational-games example:
A researcher wants a first estimate of whether playing Uno between two measurements improves understanding of greater-than and less-than. The same children complete a pre-test, play Uno in a guided session, and then complete a post-test. This can be a useful pilot design, but it is weaker for causal inference because change over time may come from factors other than the game.

## 3. Then choose the workflow

The first wizard question now uses three practical choices:

- `Plan a study`: estimate the required sample before data collection.
- `Analyze a completed study`: calculate approximate p-value, achieved power, and benchmark gaps after a study or pilot, when no previous sample plan exists.
- `Compare completed study with plan`: do the achieved-result analysis and compare the observed valid sample with a previous plan. The previous plan can be typed manually or loaded from a saved JSON configuration.

### Plan a study

Use this when the study has not been run yet and you want to estimate:

- valid analyzable participants needed
- participants who must start
- participants who must be invited

### Analyze a completed study

Use this when the study or pilot already exists and you want to estimate what the observed sample and observed effect imply.

This inverse workflow helps answer:

- Was the study underpowered?
- What approximate p-value corresponds to the observed effect?
- If the desired effect was not found, what effect was actually observed?
- How many valid participants would be needed to reach common thresholds such as `p < 0.05`, `p < 0.10`, `power >= 0.80`, or `power >= 0.90`?

### Compare completed study with plan

Use this when a sample-size plan existed before collection. Enter or load:

- planned control and intervention sample sizes, or planned total for one-group studies
- planned effect size
- planned alpha
- planned power
- observed sample sizes
- observed effect or, for binary two-group outcomes, observed event counts

The report says whether the observed sample reached the planned sample and how many valid participants were missing.

## 4. Recommended ranges and why they exist

The app now checks recommended or typical ranges. You can explicitly allow a value outside the range, but the app will record this and show it again in the `Suggestions` tab.

| Variable | Recommended or typical range | Common traditional values | Why this range is used |
|---|---|---|---|
| `alpha` | `0.01` to `0.10` | `0.05`, `0.01` | Outside this range, the evidential standard becomes unusual and should be justified. |
| `power` | `0.80` to `0.95` | `0.80`, `0.90` | Below `0.80` is often weak for confirmatory work; above `0.95` may become impractical. |
| `primary_comparisons` | `1` to `10` | `1`, `2`, `3` | Many primary comparisons often indicate the research question should be narrowed. |
| `allocation_ratio` | `0.5` to `2.0` | `1.0` | Strong imbalance often wastes information unless justified operationally. |
| `effect_size_d` | `0.10` to `1.20` | `0.20`, `0.50`, `0.80` | Tiny effects can require huge samples; huge effects should not be assumed without evidence. |
| `pre_post_correlation` | `0.30` to `0.80` | `0.50`, `0.60` | This is a common range for many educational and usability measures. |
| `response_rate` | `0.40` to `1.00` | `0.60`, `0.80`, `0.90` | Low values make recruitment fragile. |
| `completion_rate` | `0.70` to `1.00` | `0.85`, `0.90`, `0.95` | Lower values signal attrition risk. In repeated measures, completion means both measurements. |
| `usable_data_rate` | `0.80` to `1.00` | `0.90`, `0.95`, `0.98` | Low values often indicate a data-quality problem, not just a sample-size problem. |
| `extra_buffer_rate` | `0.00` to `0.20` | `0.00`, `0.05`, `0.10` | Small buffers are common; large ones may indicate weak planning assumptions. |
| `cluster_average_size` | `1` to `50` | `1`, `20`, `30` | Larger clusters make the ICC much more important. |
| `intraclass_correlation` | `0.00` to `0.20` | `0.01`, `0.05`, `0.10` | Small ICC values are common, but even `0.05` can greatly inflate sample needs. |

## 5. The difficult variable: effect size

Effect size is not a decorative number. It is the smallest effect that would matter enough to justify the intervention.

### 5.1 In two independent groups

For continuous outcomes, `effect_size_d` is the standardized difference between groups. A traditional interpretation is:

- `0.2`: small
- `0.5`: medium
- `0.8`: large

These are only rough anchors. If a learning test has a pooled standard deviation of `10` points and a `5`-point improvement would already justify using the intervention, then:

`d = 5 / 10 = 0.5`

### 5.2 In pre-test/post-test with control

Here the question is often about the difference in gain. The intervention group may improve more than the control group between pre-test and post-test.

In the Uno example:
- both groups begin with similar pre-test scores
- the intervention group plays Uno and then has a short lesson
- the control group has only the short lesson
- the effect of interest is how much more the intervention group improves

In practical terms, `effect_size_d` should represent the smallest standardized difference in gain that would matter.

### 5.3 In one-group pre-test/post-test

There is no control group, so the effect is the standardized change in the same participants.

This is useful for pilots, usability learning, or early classroom innovation studies. But interpretation is weaker because improvement may reflect practice, familiarity with the test, maturation, or ordinary teaching.

### 5.4 In post-only opinion or usability research

Sometimes there is only a survey after exposure to a system, game, or lesson. In that case, the effect size should still come from a meaningful difference, but the interpretation is often harder because there is no baseline measurement.

For example:
- if satisfaction is measured on a 1-to-5 scale
- and a difference of `0.4` points would justify changing the interface
- and the pooled standard deviation is expected to be `0.8`

then:

`d = 0.4 / 0.8 = 0.5`

## 6. Traditional numbers and why they appear so often

These values appear in the software because they are common in real research:

- `alpha = 0.05`
- `power = 0.80`
- `power = 0.90`
- `effect_size_d = 0.20, 0.50, 0.80`
- `completion_rate = 0.85` or `0.90`
- `usable_data_rate = 0.95`
- `ICC = 0.05`

They are common because they are often practical, not because they are mandatory.

## 7. Worked operational examples

### Example 1. Uno with control group and post-test comparison

Scenario:
A researcher in educational games wants to verify whether the use of Uno helps children understand greater-than and less-than. The intervention group plays Uno with guided prompts and then receives a short lesson. The control group receives only the lesson. Both groups complete a final test. The researcher expects a meaningful standardized difference of `0.5`.

Wizard choices:

- path: `Two independent groups`
- run type: `Plan required sample`
- outcome: `Continuous`
- effect size: `0.5`
- alpha: `0.05`
- power: `0.80`
- allocation ratio: `1`
- completion rate: `0.90`
- usable data rate: `0.95`

Why this wizard:
The main claim is a between-group difference after the intervention.

### Example 2. Uno with pre-test/post-test and control

Scenario:
A researcher wants a stronger learning design. Both groups complete a pre-test. The intervention group then plays Uno and attends a short lesson. The control group attends only the lesson. Both groups complete the same post-test. The researcher expects the pre-test and post-test to correlate about `0.60`, and wants to detect a meaningful standardized difference in gain of `0.4`.

Wizard choices:

- path: `Pre-test/post-test with control group`
- run type: `Plan required sample`
- outcome: `Continuous`
- effect size: `0.4`
- pre/post correlation: `0.60`
- alpha: `0.05`
- power: `0.80`
- completion rate: `0.85`

Why this wizard:
The same children are measured twice, but there is still a control group.

### Example 3. Uno with one group only

Scenario:
A researcher cannot yet recruit a comparison group and wants a pilot. The same children complete a pre-test, participate in a guided Uno session, and complete a post-test. Final adherence is defined as completing both tests. The researcher wants to detect a standardized mean change of `0.5`.

Wizard choices:

- path: `One-group pre-test/post-test`
- run type: `Plan required sample`
- outcome: `Continuous`
- effect size: `0.5`
- alpha: `0.05`
- power: `0.80`
- completion rate: `0.85`

Why this wizard:
There is no control group and the outcome is the change in the same participants.

## 8. The inverse problem

The app can also do the reverse calculation.

Example:
A Uno pilot with one group collected `28` children who completed both tests and produced an observed standardized change of `0.35`.

Wizard choices:

- path: `One-group pre-test/post-test`
- run type: `Evaluate achieved result`
- alpha: `0.05`
- observed total n: `28`
- observed effect: `0.35`

The app then estimates:

- approximate z statistic
- approximate p-value
- approximate achieved power for the observed effect

This is useful when the desired effect was not found. A non-significant result may mean:

- the intervention really had little or no effect
- the study had too little precision
- the observed effect was smaller than planned

## 9. What to do when the desired effect is not found

The absence of the desired effect does not mean there was no effect at all.

At the end of the study, it is often useful to calculate and report:

- the effect actually observed
- the approximate uncertainty around it
- whether the collected sample had enough precision for the effect you cared about

In practical terms:

- planning asks: `What effect do I want to be able to detect?`
- evaluation asks: `What effect did I actually observe, and what was this study able to show about it?`

## 10. Suggestions tab

The `Suggestions` tab is the place where the software becomes more judgmental in a helpful way.

It highlights things such as:

- low response rate
- low completion rate
- low usable-data rate
- cluster inflation
- no-control-group limitations
- values accepted outside recommended ranges

The goal is not to block the study, but to make the tradeoffs explicit.
