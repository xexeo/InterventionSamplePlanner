# Build Guide

<!-- File version: 1.0; date: 2026-05-11 -->

This guide explains how to build runnable versions of Intervention Sample Planner for Windows, Linux, and macOS.

Documentation policy: this English file is the canonical original. `build_pt.md` is its Portuguese translation.

The app is a normal Python/Tkinter application. The recommended packaging tool is PyInstaller.

## Important Rule

Build on the target operating system.

- Build Windows `.exe` on Windows.
- Build Linux executable on Linux.
- Build macOS app or executable on macOS.

PyInstaller is not a reliable cross-compiler.

## Requirements

- Python 3.10 or newer.
- Tkinter available in that Python installation.
- PyInstaller for executable builds.

Check Tkinter:

```powershell
python -c "import tkinter; print('tkinter ok')"
```

Install build dependency:

```powershell
python -m pip install -r requirements-build.txt
```

or:

```powershell
python -m pip install pyinstaller
```

## Windows Build

From the repository root:

```powershell
cd D:\GitHub\InterventionSamplePlanner
python -m PyInstaller --noconfirm --clean --windowed --name InterventionSamplePlanner run_app.py
```

Output:

```text
dist\InterventionSamplePlanner\InterventionSamplePlanner.exe
```

To build a single `.exe` file:

```powershell
python -m PyInstaller --noconfirm --clean --windowed --onefile --name InterventionSamplePlanner run_app.py
```

Output:

```text
dist\InterventionSamplePlanner.exe
```

The folder build starts faster and is easier to debug. The one-file build is easier to distribute.

## Linux Build

Install Python with Tkinter. On Debian/Ubuntu-like systems this may require:

```bash
sudo apt install python3-tk
```

Then:

```bash
python3 -m pip install -r requirements-build.txt
python3 -m PyInstaller --noconfirm --clean --windowed --name InterventionSamplePlanner run_app.py
```

Output:

```text
dist/InterventionSamplePlanner/InterventionSamplePlanner
```

If your Linux environment has no desktop display, build with `--console` for diagnostics.

## macOS Build

Use a Python installation with Tkinter support. Then:

```bash
python3 -m pip install -r requirements-build.txt
python3 -m PyInstaller --noconfirm --clean --windowed --name InterventionSamplePlanner run_app.py
```

Output is usually:

```text
dist/InterventionSamplePlanner.app
```

For local use, unsigned apps may need to be opened from Finder with Control-click > Open. For public distribution, use Apple's signing and notarization workflow.

## Build Scripts

Windows helper:

```powershell
.\scripts\build_windows.ps1
```

One-file Windows helper:

```powershell
.\scripts\build_windows.ps1 -OneFile
```

Linux/macOS helper:

```bash
./scripts/build_unix.sh
```

One-file Linux/macOS helper:

```bash
./scripts/build_unix.sh --onefile
```

## Smoke Test After Building

After building, open the executable and test:

1. Load `examples/from_sources/statsiq_teaching_method_d05.json`.
2. Click **Calculate**.
3. Confirm the summary shows `63` control and `63` intervention as the initial valid target.
4. Open the Sensitivity tab and confirm it is shown as a table.
5. Load `examples/from_sources/methodology_two_proportions_completion_45_60.json`.
6. Confirm the initial valid target is `173 + 173 = 346`.

## Troubleshooting

### PyInstaller is missing

Run:

```powershell
python -m pip install -r requirements-build.txt
```

### Tkinter is missing

Use a Python distribution that includes Tkinter. On Linux, install the OS package such as `python3-tk`.

### The app opens with a console window on Windows

Use `--windowed` or the included Windows build script.

### Antivirus warns about the executable

Unsigned PyInstaller apps can trigger warnings. For distribution outside your machine, sign the executable and distribute it from a trusted channel.

### The one-file executable starts slowly

That is normal. PyInstaller one-file builds unpack to a temporary folder before launching. Use the folder build when speed matters.

## Repository Notes

Generated `build/`, `dist/`, and `.spec` files are ignored by Git. Build outputs can exist locally without being committed.
