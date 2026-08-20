from __future__ import annotations

from pathlib import Path

import pytest

from src.reconciliation.discovery import discover_models
from src.reconciliation.metadata import resolve_metadata
from src.reconciliation import service as reconciliation_service


def _create_model(
    root: Path,
    family: str,
    model_name: str,
    *,
    readme: str = "",
    manifest: str = "",
) -> Path:
    model_root = root / family / model_name
    repository = model_root / "Repository"

    repository.mkdir(
        parents=True,
        exist_ok=True,
    )

    (repository / "config.json").write_text(
        "{}",
        encoding="utf-8",
    )

    (repository / "model.safetensors").write_bytes(
        b"test-weights"
    )

    (repository / "README.md").write_text(
        readme,
        encoding="utf-8",
    )

    (model_root / "Manifest.md").write_text(
        manifest,
        encoding="utf-8",
    )

    return model_root


def test_discover_models_ignores_service_directories(
    tmp_path: Path,
):
    _create_model(
        tmp_path,
        "Qwen",
        "Qwen3-Test",
    )

    for name in (
        "Checksums",
        "Documentation",
        "GGUF",
        "Safetensors",
    ):
        (
            tmp_path
            / "Qwen"
            / name
        ).mkdir(
            parents=True,
            exist_ok=True,
        )

    models = discover_models(
        tmp_path
    )

    assert len(models) == 1
    assert models[0].family == "Qwen"
    assert models[0].model_name == "Qwen3-Test"


def test_metadata_resolves_from_manifest(
    tmp_path: Path,
):
    _create_model(
        tmp_path,
        "Qwen",
        "Qwen3-30B-A3B-Instruct-2507",
        manifest="""
Repository:
Qwen/Qwen3-30B-A3B-Instruct-2507
""",
    )

    model = discover_models(
        tmp_path
    )[0]

    metadata = resolve_metadata(
        model
    )

    assert metadata is not None
    assert (
        metadata.model_id
        == "Qwen/Qwen3-30B-A3B-Instruct-2507"
    )
    assert metadata.source == "manifest"


def test_metadata_resolves_gemma_from_repository_readme(
    tmp_path: Path,
):
    _create_model(
        tmp_path,
        "Gemma",
        "Gemma-3-27B-Instruct",
        readme="""
model="google/gemma-3-27b-it"
""",
    )

    model = discover_models(
        tmp_path
    )[0]

    metadata = resolve_metadata(
        model
    )

    assert metadata is not None
    assert (
        metadata.model_id
        == "google/gemma-3-27b-it"
    )
    assert (
        metadata.source
        == "repository-readme"
    )


def test_metadata_resolves_kimi_from_repository_readme(
    tmp_path: Path,
):
    _create_model(
        tmp_path,
        "Kimi",
        "Kimi-K2-Instruct",
        readme="""
moonshotai/Kimi-K2-Instruct
""",
    )

    model = discover_models(
        tmp_path
    )[0]

    metadata = resolve_metadata(
        model
    )

    assert metadata is not None
    assert (
        metadata.model_id
        == "moonshotai/Kimi-K2-Instruct"
    )


def test_metadata_uses_override(
    tmp_path: Path,
):
    _create_model(
        tmp_path,
        "Unknown",
        "Unknown-Model",
    )

    model = discover_models(
        tmp_path
    )[0]

    metadata = resolve_metadata(
        model,
        override_model_id="example/model",
    )

    assert metadata is not None
    assert metadata.model_id == "example/model"
    assert metadata.source == "override"


def test_metadata_unresolved_returns_none(
    tmp_path: Path,
):
    _create_model(
        tmp_path,
        "Unknown",
        "Unknown-Model",
    )

    model = discover_models(
        tmp_path
    )[0]

    metadata = resolve_metadata(
        model
    )

    assert metadata is None


def test_reconcile_archive_skips_unresolved_model(
    tmp_path: Path,
):
    _create_model(
        tmp_path,
        "Unknown",
        "Unknown-Model",
    )

    result = reconciliation_service.reconcile_archive(
        tmp_path
    )

    assert result.valid is True
    assert result.reconciled == []
    assert len(result.skipped) == 1
    assert result.errors == []


def test_reconciliation_marks_archived_not_validated(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    _create_model(
        tmp_path,
        "Qwen",
        "Qwen3-30B-A3B-Instruct-2507",
        manifest="""
Repository:
Qwen/Qwen3-30B-A3B-Instruct-2507
""",
    )

    calls: list[str] = []

    monkeypatch.setattr(
        reconciliation_service,
        "model_exists",
        lambda model_id: False,
    )

    monkeypatch.setattr(
        reconciliation_service,
        "add_model",
        lambda model: calls.append("add_model"),
    )

    monkeypatch.setattr(
        reconciliation_service,
        "update_model_metadata",
        lambda **kwargs: calls.append(
            "update_model_metadata"
        ),
    )

    monkeypatch.setattr(
        reconciliation_service,
        "mark_archive_created",
        lambda model_id: calls.append(
            "mark_archive_created"
        ),
    )

    result = reconciliation_service.reconcile_archive(
        tmp_path
    )

    assert result.valid is True

    assert calls == [
        "add_model",
        "update_model_metadata",
        "mark_archive_created",
    ]