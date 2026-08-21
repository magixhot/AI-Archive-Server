import hashlib
import json
from pathlib import Path

from src.archive.validator import validate_archive
from src.storage.cache import get_cached_archive


def _write_archive(root: Path, model_id: str = "Qwen/Qwen3-0.6B") -> Path:
    family, model_name = model_id.split("/", 1)
    model_path = root / family / model_name
    repository = model_path / "repository"
    metadata = model_path / "metadata"
    repository.mkdir(parents=True)
    metadata.mkdir()

    model_file = repository / "config.json"
    model_file.write_text("{}", encoding="utf-8")

    digest = hashlib.sha256(model_file.read_bytes()).hexdigest()
    (metadata / "files.json").write_text(
        json.dumps([{"path": "config.json", "size": 2, "sha256": digest}]),
        encoding="utf-8",
    )
    (metadata / "model.json").write_text("{}", encoding="utf-8")
    (model_path / "manifest.json").write_text(
        json.dumps(
            {
                "archive_version": "1.0",
                "model_id": model_id,
                "family": family,
                "status": "ARCHIVED",
                "storage": {"repository": "repository/", "metadata": "metadata/"},
                "metadata": {"model": "metadata/model.json", "files": "metadata/files.json"},
            }
        ),
        encoding="utf-8",
    )
    return model_path


def test_get_cached_archive_returns_valid_model(monkeypatch, tmp_path: Path):
    import src.storage.paths as paths

    monkeypatch.setattr(paths, "MODELS_ROOT", tmp_path)
    expected = _write_archive(tmp_path)

    assert validate_archive(expected)["valid"] is True
    assert get_cached_archive("Qwen/Qwen3-0.6B") == expected


def test_get_cached_archive_preserves_model_name_after_first_separator(monkeypatch, tmp_path: Path):
    import src.storage.paths as paths

    model_id = "organization/model/variant"
    monkeypatch.setattr(paths, "MODELS_ROOT", tmp_path)
    expected = _write_archive(tmp_path, model_id)

    assert get_cached_archive(model_id) == expected


def test_get_cached_archive_rejects_missing_manifest(monkeypatch, tmp_path: Path):
    import src.storage.paths as paths

    monkeypatch.setattr(paths, "MODELS_ROOT", tmp_path)
    archive = _write_archive(tmp_path)
    (archive / "manifest.json").unlink()

    assert get_cached_archive("Qwen/Qwen3-0.6B") is None


def test_get_cached_archive_rejects_corrupt_repository(monkeypatch, tmp_path: Path):
    import src.storage.paths as paths

    monkeypatch.setattr(paths, "MODELS_ROOT", tmp_path)
    archive = _write_archive(tmp_path)
    (archive / "repository" / "config.json").write_text("changed", encoding="utf-8")

    assert validate_archive(archive)["valid"] is False
    assert get_cached_archive("Qwen/Qwen3-0.6B") is None


def test_worker_skips_download_for_cached_archive(monkeypatch, tmp_path: Path):
    import src.storage.paths as paths
    from src.download_worker import worker
    from src.model_registry.states import ModelStatus

    monkeypatch.setattr(paths, "MODELS_ROOT", tmp_path)
    _write_archive(tmp_path)

    statuses = []
    queued_batches = iter(
        [
            [(1, "Qwen/Qwen3-0.6B", "Qwen", "0.6B", "QUEUED")],
            [],
        ]
    )
    monkeypatch.setattr(
        worker,
        "get_queued_models",
        lambda: next(queued_batches),
    )
    monkeypatch.setattr(
        worker,
        "update_model_status",
        lambda model_id, status: statuses.append((model_id, status)),
    )
    monkeypatch.setattr(
        worker,
        "download_repository",
        lambda *_: (_ for _ in ()).throw(AssertionError("download must not run")),
    )

    def stop_worker(_: int) -> None:
        raise StopIteration

    monkeypatch.setattr(worker.time, "sleep", stop_worker)

    try:
        worker.process_queue()
    except StopIteration:
        pass

    assert statuses == [("Qwen/Qwen3-0.6B", ModelStatus.VALIDATED)]
