# File version: 2.1; date: 2026-05-12

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
    "InterventionSamplePlanner",
    "--add-data",
    "$root\intervention_sample_planner\explanations.json;intervention_sample_planner",
    "--add-data",
    "$root\intervention_sample_planner\web_static;intervention_sample_planner\web_static"
)

if ($OneFile) {
    $argsList += "--onefile"
}

$argsList += "run_app.py"

python -m PyInstaller @argsList
