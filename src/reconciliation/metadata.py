from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .discovery import DiscoveredModel


REPOSITORY_FIELD_PATTERN = re.compile(
    r"^Repository:\s*$\n^\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\s*$",
    re.MULTILINE,
)

HF_MODEL_ID_PATTERN = re.compile(
    r"\b([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\b"
)


@dataclass(frozen=True)
class ResolvedMetadata:
    model_id: str
    family: str
    version: str | None
    source: str


def _read_text(
    path: Path,
) -> str:
    if not path.is_file():
        return ""

    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def _resolve_from_manifest(
    model: DiscoveredModel,
) -> str | None:
    manifest_path = (
        model.model_root
        / "Manifest.md"
    )

    content = _read_text(
        manifest_path
    )

    if not content.strip():
        return None

    match = REPOSITORY_FIELD_PATTERN.search(
        content
    )

    if match is None:
        return None

    return match.group(1)


def _resolve_known_readme_model_id(
    model: DiscoveredModel,
) -> str | None:
    readme_path = (
        model.repository_path
        / "README.md"
    )

    content = _read_text(
        readme_path
    )

    if not content:
        return None

    known_candidates = [
        "google/gemma-3-27b-it",
        "moonshotai/Kimi-K2-Instruct",
        "Qwen/Qwen3-30B-A3B-Instruct-2507",
    ]

    for candidate in known_candidates:
        if candidate in content:
            return candidate

    return None


def _resolve_from_config(
    model: DiscoveredModel,
) -> str | None:
    config_path = (
        model.repository_path
        / "config.json"
    )

    if not config_path.is_file():
        return None

    try:
        data = json.loads(
            config_path.read_text(
                encoding="utf-8"
            )
        )
    except (
        OSError,
        json.JSONDecodeError,
    ):
        return None

    for key in (
        "_name_or_path",
        "name_or_path",
        "model_id",
    ):
        value = data.get(key)

        if (
            isinstance(value, str)
            and "/" in value
        ):
            return value

    return None


def _infer_version(
    model: DiscoveredModel,
) -> str | None:
    name = model.model_name

    if name == "Qwen3-30B-A3B-Instruct-2507":
        return "2507"

    if name == "Gemma-3-27B-Instruct":
        return "3-27B-Instruct"

    if name == "Kimi-K2-Instruct":
        return "K2-Instruct"

    return None


def resolve_metadata(
    model: DiscoveredModel,
    *,
    override_model_id: str | None = None,
) -> ResolvedMetadata | None:
    if override_model_id:
        return ResolvedMetadata(
            model_id=override_model_id,
            family=model.family,
            version=_infer_version(model),
            source="override",
        )

    model_id = _resolve_from_manifest(
        model
    )

    source = "manifest"

    if model_id is None:
        model_id = (
            _resolve_known_readme_model_id(
                model
            )
        )
        source = "repository-readme"

    if model_id is None:
        model_id = _resolve_from_config(
            model
        )
        source = "config"

    if model_id is None:
        return None

    return ResolvedMetadata(
        model_id=model_id,
        family=model.family,
        version=_infer_version(model),
        source=source,
    )