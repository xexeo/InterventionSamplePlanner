<!-- File version: 2.1; date: 2026-05-12 -->

# Intervention Sample Planner 2.1 Release Notes

## Main Artifacts

- Windows executable: `dist/InterventionSamplePlanner.exe`
- SHA256 checksum: `release/checksums.sha256`
- Educational manual source: `docs/educational_manual/manual.tex`
- Render deployment guide: `docs/render_deploy.md`

## Windows Executable Checksum

```text
2b007b885272d58a4fe93035831f2ef7a8e36403139f024f608be545c042791a  dist/InterventionSamplePlanner.exe
```

## Highlights

- Adds the Flask web interface and REST API as a second interface over the same Python calculation engine.
- Adds Render deployment configuration and a GitHub Actions workflow that deploys tagged commits.
- Keeps local browser save/load as JSON files without a database.
- Adds dedicated Plan / Benchmarks results and direct text, HTML, and PDF report export.
- Adds exact McNemar and Fisher support for the supported completed-study binary cases.
