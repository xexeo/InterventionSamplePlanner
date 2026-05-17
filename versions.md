<!-- File version: 2.2; date: 2026-05-17 -->

# Version History

## 2.2

- added sample-size-only reverse analysis for completed-study workflows
- added capacity tables that report minimum detectable effects for common p-value and power standards
- added reverse rows for power under common effect sizes and approximate alpha thresholds under common effect/power targets
- added allocation-scenario capacity tables when a two-group completed study provides only total sample size
- updated Tkinter and web result tables to show sample-capacity rows in `Plan / Benchmarks`
- rebuilt the Windows executable with bundled JSON explanations and web static assets

## 2.1

- added a dedicated `Plan / Benchmarks` results table for previous-plan comparison and common thresholds
- added direct report export from the desktop app as HTML and PDF, alongside the existing text report
- added exact McNemar evaluation for one-group paired binary achieved results
- added Fisher exact p-values for two-group binary achieved results with small samples or sparse cells
- clarified the ANCOVA-style interpretation for pre-test/post-test with control
- expanded cluster-randomized guidance and benchmark adjustment when cluster assumptions are entered
- updated `explanations.json`, the JSON schema, tests, screenshots, README files, and build/developer documentation
- added release screenshots under `docs/screenshots`
- added SHA256 checksum support for the generated Windows executable release artifact
- added Flask web interface and REST API as a second interface over the same calculation engine
- added Render deployment configuration and a GitHub Actions workflow that deploys tagged commits
- added detailed Render deployment documentation
- added browser-side local JSON save/load and recommended-range override checks to the web client

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
