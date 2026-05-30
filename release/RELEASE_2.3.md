<!-- File version: 2.3; date: 2026-05-18 -->

# Intervention Sample Planner 2.3 Release Notes

## Main Artifacts

- Windows executable: `dist/InterventionSamplePlanner.exe`
- SHA256 checksum: `release/checksums.sha256`
- Educational manual source: `docs/educational_manual/manual.tex`
- Educational manual PDF: `docs/educational_manual/manual.pdf`
- Render deployment guide: `docs/render_deploy.md`

## Windows Executable Checksum

```text
5E85F7688F70AB2CA74C712F3BC79AAF33E6512DE7706307B392D5F18D1C613C  dist/InterventionSamplePlanner.exe
```

## Highlights

- Raises the application to `ISP v2.3`.
- Adds `One-group post-intervention survey` for opinion-only studies after an intervention.
- Adds planning by favorable-response proportion using confidence level and margin of error.
- Adds planning by mean survey score using expected standard deviation and mean margin of error.
- Adds completed-survey evaluation from Likert/star/numeric response histograms, favorable counts, or mean/SD summaries.
- Reports valid response counts, NA/missing counts, favorable proportions, Wilson confidence intervals, and mean-score summaries where available.
- Updates the Tkinter interface, web interface, REST output, JSON schema, help text, README files, changelog, version notes, developer notes, theory introduction, and educational manual source.
- Rebuilds the educational manual PDF with LuaLaTeX.
- Rebuilds the Windows executable with bundled explanation and web static assets.
