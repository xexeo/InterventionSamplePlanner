<!-- File version: 2.2; date: 2026-05-17 -->

# Intervention Sample Planner 2.2 Release Notes

## Main Artifacts

- Windows executable: `dist/InterventionSamplePlanner.exe`
- SHA256 checksum: `release/checksums.sha256`
- Educational manual source: `docs/educational_manual/manual.tex`
- Educational manual PDF: `docs/educational_manual/manual.pdf`
- Render deployment guide: `docs/render_deploy.md`

## Windows Executable Checksum

```text
1AEF2A7C0ADE2065AC9A20CD12E51AA691901FD3047A79AA52B6BC1F2887A666  dist/InterventionSamplePlanner.exe
```

## Highlights

- Raises the application to `ISP v2.2`.
- Adds sample-size-only reverse analysis for completed studies when the observed effect is not yet known or cannot be entered as a single value.
- Adds capacity rows that show minimum detectable effects, power for common effects, and alpha thresholds for common reporting standards.
- Adds allocation scenarios for completed two-group studies when only total sample size is available.
- Updates the Tkinter interface, web interface, REST output, JSON schema, help text, README files, changelog, version notes, developer notes, theory introduction, and educational manual source.
- Rebuilds the educational manual PDF with LuaLaTeX.
- Rebuilds the Windows executable with bundled explanation and web static assets.
