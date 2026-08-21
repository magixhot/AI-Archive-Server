from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.model_registry import recovery


def _create_managed_archive(
    root: Path,
    *,
    model_id: str = "Qwen/Qwen3-0.6B",
    family: str = "Qwen",
    version: str = "0.6B",
) -> Path:
    model_root = root / family / model_id.split("/", 1)[1]
    repository = model_root / "repository"

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

    manifest = {
        "archive_version": "1.0",
        "model_id": model_id,
        "family": family,
        "version": version,
        "status": "ARCHIVED",
    }

    (model_root / "manifest.json").write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    return model_root


def test_reconcile_managed_archive_restores_archived_model(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    archive_root = tmp_path / "models"

    model_root = _create_managed_archive(
        archive_root
    )

    added_models = []
    metadata_calls = []
    archived_calls = []

    monkeypatch.setattr(
        recovery,
        "model_exists",
        lambda model_id: False,
    )

    monkeypatch.setattr(
        recovery,
        "add_model",
        lambda model: added_models.append(model),
    )

    monkeypatch.setattr(
        recovery,
        "update_model_metadata",
        lambda **kwargs: metadata_calls.append(kwargs),
    )

    monkeypatch.setattr(
        recovery,
        "mark_archive_created",
        lambda model_id: archived_calls.append(model_id),
    )

    result = recovery.reconcile_managed_archive(
        archive_root
    )

    assert result.valid is True
    assert result.managed == [
        "Qwen/Qwen3-0.6B"
    ]
    assert result.errors == []

    assert len(added_models) == 1

    model = added_models[0]

    assert model.model_id == "Qwen/Qwen3-0.6B"
    assert model.family == "Qwen"
    assert model.version == "0.6B"
    assert model.status == "ARCHIVED"
    assert model.storage_path == str(model_root)

    assert metadata_calls == [
        {
            "model_id": "Qwen/Qwen3-0.6B",
            "storage_path": str(model_root),
            "size_bytes": len(b"{}") + len(b"test-weights"),
            "sha256": None,
        }
    ]

    assert archived_calls == [
        "Qwen/Qwen3-0.6B"
    ]


def test_reconcile_managed_archive_is_idempotent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    archive_root = tmp_path / "models"

    _create_managed_archive(
        archive_root
    )

    added_models = []

    monkeypatch.setattr(
        recovery,
        "model_exists",
        lambda model_id: True,
    )

    monkeypatch.setattr(
        recovery,
        "add_model",
        lambda model: added_models.append(model),
    )

    monkeypatch.setattr(
        recovery,
        "update_model_metadata",
        lambda **kwargs: None,
    )

    monkeypatch.setattr(
        recovery,
        "mark_archive_created",
        lambda model_id: None,
    )

    result = recovery.reconcile_managed_archive(
        archive_root
    )

    assert result.valid is True
    assert result.managed == [
        "Qwen/Qwen3-0.6B"
    ]
    assert added_models == []


def test_reconcile_managed_archive_skips_invalid_manifest(
    tmp_path: Path,
):
    model_root = (
        tmp_path
        / "models"
        / "Qwen"
        / "Broken"
    )

    repository = model_root / "repository"

    repository.mkdir(
        parents=True,
        exist_ok=True,
    )

    (model_root / "manifest.json").write_text(
        json.dumps(
            {
                "model_id": "invalid-model-id",
                "family": "Qwen",
            }
        ),
        encoding="utf-8",
    )

    result = recovery.reconcile_managed_archive(
        tmp_path / "models"
    )

    assert result.valid is True
    assert result.managed == []
    assert len(result.skipped) == 1
    assert "invalid model_id" in result.skipped[0]


def test_recover_registry_combines_sources_when_empty(
    monkeypatch: pytest.MonkeyPatch,
):
    calls = []

    monkeypatch.setattr(
        recovery,
        "bootstrap_registry",
        lambda: calls.append("bootstrap"),
    )

    monkeypatch.setattr(
        recovery,
        "get_all_models",
        lambda: [],
    )

    monkeypatch.setattr(
        recovery,
        "reconcile_archive",
        lambda root: SimpleNamespace(
            reconciled=["historical/model"],
            skipped=["historical-skip"],
            errors=[],
        ),
    )

    monkeypatch.setattr(
        recovery,
        "reconcile_managed_archive",
        lambda root: recovery.RecoveryResult(
            managed=["managed/model"],
            skipped=["managed-skip"],
        ),
    )

    result = recovery.recover_registry(
        historical_archive_root="/historical",
        managed_archive_root="/managed",
    )

    assert calls == ["bootstrap"]
    assert result.valid is True
    assert result.historical == [
        "historical/model"
    ]
    assert result.managed == [
        "managed/model"
    ]
    assert result.skipped == [
        "historical-skip",
        "managed-skip",
    ]


def test_recover_registry_skips_when_registry_not_empty(
    monkeypatch: pytest.MonkeyPatch,
):
    calls = []

    monkeypatch.setattr(
        recovery,
        "bootstrap_registry",
        lambda: calls.append("bootstrap"),
    )

    monkeypatch.setattr(
        recovery,
        "get_all_models",
        lambda: [
            {
                "model_id": "Qwen/Qwen3-0.6B"
            }
        ],
    )

    monkeypatch.setattr(
        recovery,
        "reconcile_archive",
        lambda root: pytest.fail(
            "historical reconciliation must not run"
        ),
    )

    monkeypatch.setattr(
        recovery,
        "reconcile_managed_archive",
        lambda root: pytest.fail(
            "managed reconciliation must not run"
        ),
    )

    result = recovery.recover_registry()

    assert calls == ["bootstrap"]
    assert result.valid is True
    assert result.historical == []
    assert result.managed == []
    assert result.skipped == [
        "registry already contains models"
    ]