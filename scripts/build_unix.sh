#!/usr/bin/env bash
# File version: 2.2; date: 2026-05-17
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ARGS=(
  --noconfirm
  --clean
  --windowed
  --name
  InterventionSamplePlanner
  --add-data
  "$ROOT/intervention_sample_planner/explanations.json:intervention_sample_planner"
  --add-data
  "$ROOT/intervention_sample_planner/web_static:intervention_sample_planner/web_static"
)

if [[ "${1:-}" == "--onefile" ]]; then
  ARGS+=(--onefile)
fi

python3 -m PyInstaller "${ARGS[@]}" run_app.py
