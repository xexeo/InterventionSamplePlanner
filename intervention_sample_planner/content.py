"""Load explanation and recommendation content for the application."""

# File version: 2.2; date: 2026-05-17

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_CONTENT_PATH = Path(__file__).with_name("explanations.json")
_CACHE: dict[str, Any] | None = None


def load_content() -> dict[str, Any]:
    global _CACHE
    if _CACHE is None:
        _CACHE = json.loads(_CONTENT_PATH.read_text(encoding="utf-8"))
    return _CACHE


def get_field_content(language: str, field: str) -> dict[str, Any]:
    content = load_content()
    language_block = content.get(language, content["en"])
    return language_block.get("fields", {}).get(field, {})


def get_design_content(language: str, design: str) -> dict[str, Any]:
    content = load_content()
    language_block = content.get(language, content["en"])
    return language_block.get("designs", {}).get(design, {})


def get_general_content(language: str, key: str, default: str = "") -> str:
    content = load_content()
    language_block = content.get(language, content["en"])
    return str(language_block.get("general", {}).get(key, default))
