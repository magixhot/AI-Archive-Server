from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from pathlib import Path
import shutil


IGNORED_PARTS = {".cache", ".git", "__pycache__"}


@dataclass
class SyncResult:
    """Outcome of a one-way archive synchronization."""

    dry_run: bool
    copied_files: list[str] = field(default_factory=list)
    unchanged_files: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "dry_run": self.dry_run,
            "copied_files": self.copied_files,
            "unchanged_files": self.unchanged_files,
            "errors": self.errors,
        }


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def _iter_source_files(source_root: Path):
    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue

        relative_path = path.relative_to(source_root)

        if any(part in IGNORED_PARTS for part in relative_path.parts):
            continue

        yield path, relative_path


def _is_same_file(source: Path, target: Path) -> bool:
    return (
        target.is_file()
        and source.stat().st_size == target.stat().st_size
        and _file_sha256(source) == _file_sha256(target)
    )


def sync_archive(
    source_root: str | Path,
    target_root: str | Path,
    *,
    dry_run: bool = True,
) -> SyncResult:
    """Synchronize archive files from ``source_root`` to ``target_root``.

    Synchronization is deliberately additive: it copies new or changed source
    files and never removes files from the target.  This protects archived
    originals and makes the default dry-run safe for routine planning.
    """

    source_root = Path(source_root).resolve()
    target_root = Path(target_root).resolve()
    result = SyncResult(dry_run=dry_run)

    if not source_root.is_dir():
        result.errors.append(f"Source archive does not exist: {source_root}")
        return result

    if source_root == target_root:
        result.errors.append("Source and target archives must be different directories.")
        return result

    if (
        target_root.is_relative_to(source_root)
        or source_root.is_relative_to(target_root)
    ):
        result.errors.append("Source and target archives must not contain one another.")
        return result

    for source_path, relative_path in _iter_source_files(source_root):
        target_path = target_root / relative_path
        display_path = relative_path.as_posix()

        try:
            if _is_same_file(source_path, target_path):
                result.unchanged_files.append(display_path)
                continue

            result.copied_files.append(display_path)

            if not dry_run:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path)
        except OSError as error:
            result.errors.append(f"{display_path}: {error}")

    return result
