# File version: 1.0; date: 2026-05-11

param(
    [switch]$OneFile
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

$argsList = @(
    "--noconfirm",
    "--clean",
    "--windowed",
    "--name",
    "InterventionSamplePlanner"
)

if ($OneFile) {
    $argsList += "--onefile"
}

$argsList += "run_app.py"

python -m PyInstaller @argsList
