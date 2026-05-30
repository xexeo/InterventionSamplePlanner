<!-- File version: 2.4; date: 2026-05-30 -->

# Changelog

## 2.4 - 2026-05-30

### Added

- Stratified post-intervention survey study type for opinion surveys that need demographic representation.
- Stratified wizard path, configuration fields, REST output, schema, help text, and tests.
- Per-stratum planning rows with population share, valid target, assigned/starters, invitations, and optional weights.
- Per-stratum achieved-result evaluation with observed share, representation ratio, favorable proportion, and status flags.

### Changed

- Version metadata now reports `ISP v2.4`.
- Tkinter and web interfaces now expose the same stratified survey variables and show stratified rows in result tables.
- Suggestions now warn about sparse strata, under-representation, and unstable weights.

## 2.3 - 2026-05-18

### Added

- One-group post-intervention survey study type for MEEGA+-style, Likert, star, and bounded numeric opinion surveys.
- Survey planning for favorable-response proportions using confidence level and margin of error.
- Survey planning for mean scores using confidence level, expected standard deviation, and mean margin of error.
- Survey evaluation from JSON response histograms, favorable counts, or mean plus standard deviation.
- Wilson confidence intervals for favorable-response proportions and descriptive confidence intervals for mean survey scores.
- Survey-specific guidance in Tkinter, the web interface, REST output, schema, explanations, tests, README files, and the educational manual.

### Changed

- Version metadata now reports `ISP v2.3`.
- Survey workflows hide p-value/power inputs where the relevant task is descriptive estimation rather than causal hypothesis testing.
- Suggestions now warn when a post-intervention survey is being used as evidence of user opinion rather than evidence of intervention effect.

## 2.2 - 2026-05-17

### Added

- Sample-size-only reverse analysis for completed-study workflows.
- Capacity rows that report minimum detectable effects for common `p`/alpha and power combinations.
- Reverse rows that report approximate power for common effect sizes and approximate alpha thresholds needed for common effect/power targets.
- Allocation-scenario capacity tables when two-group completed studies provide only a total sample size.

### Changed

- Completed-study mode no longer requires an observed effect when the user only wants to evaluate what the achieved sample size can support.
- Tkinter and web result tables now display sample-capacity rows in the `Plan / Benchmarks` tab.
- Rebuilt the Windows executable with bundled `explanations.json` and `web_static` assets.

## 2.1 - 2026-05-12

### Added

- Dedicated `Plan / Benchmarks` results table for completed-study evaluation.
- HTML and PDF report export directly from the Tkinter app.
- Exact McNemar evaluation for one-group paired binary before/after results.
- Fisher exact p-values for two-group binary achieved results when event counts are available.
- Screenshot assets in `docs/screenshots`.
- SHA256 checksum file for the generated Windows executable release artifact.
- Screenshot capture helper for release documentation.
- Flask REST API and static web client as a second interface.
- Render Blueprint and tag-triggered GitHub Actions deployment workflow.
- Detailed Render deployment guide.
- Browser-side JSON save/load for local study files without a database.

### Changed

- Version metadata now reports `ISP v2.1`.
- Completed-study suggestions now explain exact p-values, underpowered results, previous-plan gaps, and benchmark gaps more explicitly.
- Pre-test/post-test with control now explains its ANCOVA-style approximation more clearly.
- Clustered designs now receive stronger warnings about cluster-level planning and analysis.
- Documentation, JSON schema, examples coverage, README files, and developer/build notes were updated for v2.1.
- The project now documents two supported interfaces: Tkinter desktop and Flask web.
- The web client now mirrors the recommended-range override flow used by the desktop app.

### Fixed

- Small or sparse two-group binary achieved results now use the exact Fisher p-value as the reported p-value.
- One-group paired binary achieved results no longer require a continuous observed effect size.
