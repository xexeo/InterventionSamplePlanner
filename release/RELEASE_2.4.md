<!-- File version: 2.4; date: 2026-05-30 -->

# Intervention Sample Planner 2.4 Release Notes

## Artifacts

- Windows executable: `dist/InterventionSamplePlanner.exe`
- SHA256 checksum: `release/checksums.sha256`
- Educational manual: `docs/educational_manual/manual.pdf`

## Checksum

```text
6018D9075B643C9706A11B83FF1B66CD5CE28CECF394E887AD7185D80EC1FA7D  dist/InterventionSamplePlanner.exe
```

## Main changes

- Raises the application to `ISP v2.4`.
- Adds stratified post-intervention opinion survey planning and evaluation.
- Adds per-stratum planning for valid responses, starters, invitations, expected shares, and optional weights.
- Adds achieved-study evaluation for observed strata, including representation ratios, missing strata, under-representation, over-representation, and per-stratum favorable proportions when available.
- Exposes the new stratified survey path in the Python API, Tkinter interface, Flask REST API, web client, JSON schema, explanations JSON, tests, README files, developer notes, operational theory files, and educational manual.
