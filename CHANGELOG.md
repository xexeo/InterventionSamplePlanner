<!-- File version: 2.1; date: 2026-05-12 -->

# Changelog

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
