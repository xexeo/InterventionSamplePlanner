<!-- File version: 2.2; date: 2026-05-17 -->

# Build Guide

## Python app

```powershell
cd D:\GitHub\InterventionSamplePlanner
python -m unittest discover -s tests
python run_app.py
```

## Windows executable

The executable is built with PyInstaller. Because `ISP v2.2` depends on `intervention_sample_planner/explanations.json`, the build command must include that file.

Example:

```powershell
python -m PyInstaller --noconfirm --clean --windowed --onefile --name InterventionSamplePlanner --add-data "intervention_sample_planner\explanations.json;intervention_sample_planner" --add-data "intervention_sample_planner\web_static;intervention_sample_planner\web_static" run_app.py
```

After building a Windows release executable, create or verify the SHA256 checksum:

```powershell
Get-FileHash .\dist\InterventionSamplePlanner.exe -Algorithm SHA256
```

The release checksum tracked in the repository is stored in:

```text
release/checksums.sha256
```

## Report export

The desktop app can export the current result as text, HTML, or PDF. The PDF writer is intentionally simple and local; it does not require a browser or external PDF dependency.

## Web interface

The web interface uses Flask for the REST API and local static files for the browser client.

```powershell
python -m pip install -r requirements.txt
python -m flask --app intervention_sample_planner.web_app run
```

For Render deployment, see [docs/render_deploy.md](docs/render_deploy.md).

## Screenshots

Release screenshots can be regenerated on Windows with:

```powershell
python scripts\capture_screenshots.py
```

## Educational manual

The educational manual uses LuaLaTeX.

Build:

```powershell
cd D:\GitHub\InterventionSamplePlanner\docs\educational_manual
.\compile_manual.bat
```

Clean auxiliary files and keep the PDF:

```powershell
.\compile_manual.bat clean
```

Clean all generated files and keep only the source files:

```powershell
.\compile_manual.bat clean-all
```
