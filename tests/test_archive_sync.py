from pathlib import Path

from src.archive_sync import sync_archive


def _create_archive(root: Path) -> None:
    model = root / "Qwen" / "Qwen3-0.6B"
    repository = model / "repository"
    metadata = model / "metadata"
    repository.mkdir(parents=True)
    metadata.mkdir()
    (model / "manifest.json").write_text(
        '{"model_id": "Qwen/Qwen3-0.6B"}',
        encoding="utf-8",
    )
    (metadata / "files.json").write_text("[]", encoding="utf-8")
    (repository / "config.json").write_text(
        '{"model_type": "qwen3"}',
        encoding="utf-8",
    )
    (repository / ".cache").mkdir()
    (repository / ".cache" / "ignored.txt").write_text("ignore me", encoding="utf-8")


def test_sync_archive_dry_run_does_not_write_files(tmp_path: Path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    _create_archive(source)

    result = sync_archive(source, target)

    assert result.valid
    assert result.dry_run
    assert "Qwen/Qwen3-0.6B/repository/config.json" in result.copied_files
    assert not target.exists()


def test_sync_archive_copies_changes_and_preserves_target_only_files(tmp_path: Path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    _create_archive(source)
    target.mkdir()
    target_only = target / "legacy" / "note.txt"
    target_only.parent.mkdir()
    target_only.write_text("preserve me", encoding="utf-8")

    result = sync_archive(source, target, dry_run=False)

    assert result.valid
    assert not result.dry_run
    assert (
        target / "Qwen" / "Qwen3-0.6B" / "repository" / "config.json"
    ).exists()
    assert not (target / "Qwen" / "Qwen3-0.6B" / "repository" / ".cache").exists()
    assert target_only.read_text(encoding="utf-8") == "preserve me"

    repeated = sync_archive(source, target, dry_run=False)

    assert not repeated.copied_files
    assert "Qwen/Qwen3-0.6B/repository/config.json" in repeated.unchanged_files


def test_sync_archive_rejects_same_source_and_target(tmp_path: Path):
    _create_archive(tmp_path)

    result = sync_archive(tmp_path, tmp_path)

    assert not result.valid
    assert result.errors == ["Source and target archives must be different directories."]


def test_sync_archive_rejects_nested_archives(tmp_path: Path):
    source = tmp_path / "source"
    _create_archive(source)

    result = sync_archive(source, source / "replica")

    assert not result.valid
    assert result.errors == ["Source and target archives must not contain one another."]
