<!-- File version: 2.0; date: 2026-05-11 -->

# Build Guide

## Python app

```powershell
cd D:\GitHub\InterventionSamplePlanner
python -m unittest discover -s tests
python run_app.py
```

## Windows executable

The executable is built with PyInstaller. Because `ISP v2.0` now depends on `intervention_sample_planner/explanations.json`, the build command must include that file.

Example:

```powershell
python -m PyInstaller --noconfirm --clean --windowed --onefile --name InterventionSamplePlanner --add-data "intervention_sample_planner\explanations.json;intervention_sample_planner" run_app.py
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
