"""Local archive cache lookup for downloaded Hugging Face models."""

from __future__ import annotations

import json
from pathlib import Path

from src.archive.validator import validate_archive

from .paths import get_model_path


def get_cached_archive(model_id: str) -> Path | None:
    """Return a valid cached archive for model_id."""

    try:
        family, model_name = model_id.split("/", 1)
    except ValueError:
        return None

    model_path = get_model_path(family, model_name)
    manifest_path = model_path / "manifest.json"

    if not model_path.is_dir() or not manifest_path.is_file():
        return None

    try:
        with manifest_path.open(encoding="utf-8") as manifest_file:
            manifest = json.load(manifest_file)
    except (json.JSONDecodeError, OSError):
        return None

    if manifest.get("model_id") != model_id:
        return None

    validation = validate_archive(model_path)

    if not validation["valid"]:
        return None

    return model_path