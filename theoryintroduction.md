<!-- File version: 2.4; date: 2026-05-30 -->

# Operational Theory Summary for ISP v2.4

This operational manual explains how to use `ISP v2.4` in a practical way. It is shorter than the educational LaTeX manual, but it is written to support real decisions in the app.

## 1. Current capabilities in v2.4

`ISP v2.4` supports the original two-group planning workflow, completed-study workflows, and post-intervention opinion survey workflows:

- `Two independent groups`
- `Pre-test/post-test with control group`
- `One-group pre-test/post-test`
- `One-group post-intervention survey`
- `Stratified post-intervention survey`
- `Plan required sample`
- `Evaluate achieved result`
- `Compare completed study with plan`
- recommended ranges with explicit override
- explanations in `intervention_sample_planner/explanations.json`
- a dedicated `Suggestions` tab
- sample-capacity reverse analysis when only the achieved sample size is available
- survey precision planning and completed-survey evaluation for Likert, star, and bounded numeric opinion scales
- stratified survey planning and evaluation for demographic representation

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

### Path D. One-group post-intervention survey

Use this when participants only answer an opinion, experience, usability, or perceived-learning questionnaire after the intervention. This is common in MEEGA+-style educational-game evaluations, Likert questionnaires, star ratings, and post-use usability forms.

Educational-games example:
After a guided Uno learning session, a researcher asks students whether the activity was easy to learn, fun, useful, and whether it helped them understand greater-than and less-than. There is no pre-test and no control group in this path. The result can support a descriptive statement such as "with 95% confidence, at least about 70% of valid respondents gave a favorable answer," but it cannot prove that Uno caused learning.

### Path E. Stratified post-intervention survey

Use this when the same post-intervention opinion survey should represent demographic classes. A stratum is a planned class such as age band, school type, region, prior experience, or gender. The point is not to prove causality; it is to avoid a descriptive claim being dominated by the easiest respondents to recruit.

Educational-games example:
After a guided Uno learning session, a researcher wants the opinion survey to represent children aged `8-10`, `11-13`, and `14-16`. If the population is 30%, 40%, and 30% in those bands, proportional allocation follows those shares. If the researcher also wants each band to be visible, the minimum-per-stratum option can require at least 30 valid responses per band. In the achieved-result workflow, the app checks whether each band is under target, under-represented, or over-represented.

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
| `survey_expected_proportion` | `0.30` to `0.90` | `0.50`, `0.70`, `0.80` | `0.50` is conservative for margin-of-error planning; higher values should come from a pilot or previous evidence. |
| `survey_margin_of_error` | `0.03` to `0.15` | `0.05`, `0.10` | Opinion surveys often report precision in percentage points. Smaller margins require many more respondents. |
| `survey_favorable_threshold` | inside the scale | `4` on a 1-to-5 scale | The threshold should match the verbal meaning of the scale, such as "agree" or better. |
| `survey_mean_margin_of_error` | `0.05` to `1.00` scale points | `0.20`, `0.30`, `0.50` | Mean precision should be small enough to matter on the scale but feasible for the expected sample. |
| `stratified_min_per_stratum` | `10` to `100` | `20`, `30`, `50` | Very small strata produce unstable subgroup percentages; very large minimums can make recruitment infeasible. |
| `stratified_target_total` | blank or feasible total | blank, `100`, `200`, `400` | Leave blank when precision should determine the total; enter a value when the feasible sample is externally fixed. |

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

Sometimes there is only a survey after exposure to a system, game, or lesson. In `one_group_post_survey`, the app does not ask for `effect_size_d`, because the main output is not a causal comparison. The practical decision is usually the desired precision of a descriptive claim.

For example:
- if agreement is measured on a 1-to-5 Likert scale
- and scores `4` and `5` mean favorable responses
- and the researcher wants a margin of error of about `0.10`

then the planning question is how many valid respondents are needed so the confidence interval around the favorable-response proportion is narrow enough. If the researcher instead wants to report a mean score, the app uses the expected standard deviation and desired mean margin of error.

This path should not be interpreted as "the intervention worked." It supports statements about what respondents reported after the intervention.

## 6. Traditional numbers and why they appear so often

These values appear in the software because they are common in real research:

- `alpha = 0.05`
- `power = 0.80`
- `power = 0.90`
- `effect_size_d = 0.20, 0.50, 0.80`
- `completion_rate = 0.85` or `0.90`
- `usable_data_rate = 0.95`
- `ICC = 0.05`
- `survey_margin_of_error = 0.05` or `0.10`
- `survey_expected_proportion = 0.50` when no better prior estimate exists

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

### Example 4. Uno post-intervention opinion survey

Scenario:
After a classroom activity using Uno, the researcher asks children to answer a short questionnaire about the game. One item says: "The game helped me understand greater-than and less-than." The response scale is 1 to 5, where `1` means strongly disagree, `3` means neither agree nor disagree, `4` means agree, and `5` means strongly agree. The researcher wants to plan enough valid respondents to describe the favorable-response proportion with a 95% confidence interval and about 10 percentage points of margin of error.

Wizard choices:

- path: `One-group post-intervention survey`
- run type: `Plan required sample`
- survey analysis goal: `Favorable-response proportion`
- alpha: `0.05`
- survey scale minimum: `1`
- survey scale maximum: `5`
- survey scale points: `5`
- favorable threshold: `4`
- expected favorable proportion: `0.50` if there is no pilot
- margin of error: `0.10`
- completion rate: `0.90`
- usable data rate: `0.95`

Why this wizard:
There is no control group and no before/after measurement. The claim is about the precision of reported opinions after the activity.

### Example 5. Uno stratified post-intervention opinion survey

Scenario:
The same Uno activity will be used in a mixed school program. The researcher knows that the intended population is about 30% children aged `8-10`, 40% aged `11-13`, and 30% aged `14-16`. A simple overall survey could accidentally over-sample older children if they answer faster. The researcher therefore wants the opinion claim to be checked by age band.

Wizard choices:

- path: `Stratified post-intervention survey`
- run type: `Plan required sample`
- survey analysis goal: `Favorable-response proportion`
- alpha: `0.05`
- margin of error: `0.10`
- strata definition: `{"age_8_10": {"label": "Age 8-10", "population_proportion": 0.30}, "age_11_13": {"label": "Age 11-13", "population_proportion": 0.40}, "age_14_16": {"label": "Age 14-16", "population_proportion": 0.30}}`
- allocation method: `minimum_per_stratum` when each age band must be visible, or `proportional` when the overall estimate is the main goal
- minimum per stratum: `30`
- use weights: `true`

Why this wizard:
The study is still descriptive, but the claim is meant to represent a population with known classes. The app plans valid responses per stratum and later checks whether each class was under target or under-represented.

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

If the pilot has only the achieved sample size and no defensible observed effect yet, the app now gives a capacity table instead of pretending there is one unique answer. For example, with `28` complete one-group pre/post pairs it can report the minimum detectable effect for `p < 0.05` with `80%` power, the power for common effects such as `d = 0.20`, `0.50`, and `0.80`, and the approximate alpha threshold needed for common effect/power targets. For two-group studies with only a total `n`, it also compares common allocations such as `1:1`, `2:1`, and `1:2`.

For a post-intervention survey, the inverse interpretation is different. If the researcher enters only the achieved number of valid respondents, the app estimates the approximate current margin of error for a favorable proportion. If the researcher enters a histogram such as `{"1": 2, "2": 4, "3": 10, "4": 18, "5": 26, "NA": 3}`, the app reports the valid denominator, NA count, favorable count, favorable proportion, Wilson confidence interval, and mean score. This supports a descriptive conclusion such as: "Most valid respondents were favorable, but the lower confidence bound is the conservative part of the claim."

For a stratified survey, the inverse interpretation adds representation. If the researcher enters achieved stratum data, the app reports the overall survey result and a stratum table with expected share, observed share, representation ratio, optional weight, and a status such as `under target`, `under-represented`, `over-represented`, or `ok`. This helps decide whether the overall opinion claim can be stated broadly or should be qualified, for example: "The younger age band was under-represented, so the result mainly reflects older respondents."

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
- post-intervention survey limitations when the evidence is descriptive rather than causal
- values accepted outside recommended ranges

The goal is not to block the study, but to make the tradeoffs explicit.
