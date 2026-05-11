<!-- File version: 2.0; date: 2026-05-11 -->

# Version History

## 2.0

- added research-path selection at the start of the wizard
- added `Pre-test/post-test with control group`
- added `One-group pre-test/post-test`
- added `Evaluate achieved result` inverse workflow
- added three explicit workflow choices: plan a study, analyze a completed study, and compare a completed study with a previous plan
- added loading of saved JSON plans into the plan-comparison workflow
- added binary achieved-result event counts, observed rates, benchmark gaps, and missing-sample estimates for common p-value and power thresholds
- added recommended ranges with explicit override
- moved long-form variable explanations to `intervention_sample_planner/explanations.json`
- added the `Suggestions` tab
- expanded the API, schema, tests, and operational documentation
- updated the educational manual and the manual build scripts for LuaLaTeX cleaning

## 1.0

- initial local API and Tkinter app
- support for two independent groups
- support for continuous and binary outcomes
- support for attrition, response, finite population, and cluster corrections
- support for sensitivity analysis and JSON configuration
