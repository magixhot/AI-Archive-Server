from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from src.model_registry.bootstrap import bootstrap_registry
from src.model_registry.models import ModelRecord
from src.model_registry.service import (
    add_model,
    get_all_models,
    mark_archive_created,
    model_exists,
    update_model_metadata,
)
from src.reconciliation.service import reconcile_archive


BASE_DIR = Path(__file__).resolve().parents[2]

HISTORICAL_ARCHIVE_ROOT = Path("/app/02_Models")
MANAGED_ARCHIVE_ROOT = BASE_DIR / "AI-Archive" / "models"


@dataclass
class RecoveryResult:
    historical: list[str] = field(default_factory=list)
    managed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "historical": self.historical,
            "managed": self.managed,
            "skipped": self.skipped,
            "errors": self.errors,
        }


def _repository_size(repository_path: Path) -> int:
    total_size = 0

    if not repository_path.is_dir():
        return total_size

    for path in repository_path.rglob("*"):
        if path.is_file():
            total_size += path.stat().st_size

    return total_size


def reconcile_managed_archive(
    archive_root: str | Path,
) -> RecoveryResult:
    result = RecoveryResult()

    archive_root = Path(archive_root)

    if not archive_root.is_dir():
        return result

    for family_path in sorted(archive_root.iterdir()):
        if not family_path.is_dir():
            continue

        for model_root in sorted(family_path.iterdir()):
            if not model_root.is_dir():
                continue

            manifest_path = model_root / "manifest.json"

            if not manifest_path.is_file():
                result.skipped.append(
                    f"{model_root}: manifest.json missing"
                )
                continue

            try:
                manifest = json.loads(
                    manifest_path.read_text(
                        encoding="utf-8"
                    )
                )

                model_id = manifest.get("model_id")
                family = manifest.get("family")
                version = manifest.get("version")

                if not isinstance(model_id, str) or "/" not in model_id:
                    result.skipped.append(
                        f"{model_root}: invalid model_id"
                    )
                    continue

                repository_path = model_root / "repository"

                if not repository_path.is_dir():
                    result.skipped.append(
                        f"{model_root}: repository missing"
                    )
                    continue

                storage_path = str(model_root)
                size_bytes = _repository_size(
                    repository_path
                )

                if not model_exists(model_id):
                    add_model(
                        ModelRecord(
                            model_id=model_id,
                            family=family,
                            version=version,
                            status="ARCHIVED",
                            storage_path=storage_path,
                            size_bytes=size_bytes,
                        )
                    )

                update_model_metadata(
                    model_id=model_id,
                    storage_path=storage_path,
                    size_bytes=size_bytes,
                    sha256=None,
                )

                mark_archive_created(model_id)

                result.managed.append(model_id)

            except Exception as error:
                result.errors.append(
                    f"{model_root}: "
                    f"{type(error).__name__}: {error}"
                )

    return result


def recover_registry(
    *,
    historical_archive_root: str | Path = HISTORICAL_ARCHIVE_ROOT,
    managed_archive_root: str | Path = MANAGED_ARCHIVE_ROOT,
) -> RecoveryResult:
    bootstrap_registry()

    existing_models = get_all_models()

    if existing_models:
        return RecoveryResult(
            skipped=[
                "registry already contains models"
            ]
        )

    result = RecoveryResult()

    historical = reconcile_archive(
        historical_archive_root
    )

    result.historical.extend(
        historical.reconciled
    )
    result.skipped.extend(
        historical.skipped
    )
    result.errors.extend(
        historical.errors
    )

    managed = reconcile_managed_archive(
        managed_archive_root
    )

    result.managed.extend(
        managed.managed
    )
    result.skipped.extend(
        managed.skipped
    )
    result.errors.extend(
        managed.errors
    )

    return result


def main() -> None:
    result = recover_registry()

    print(
        "Registry recovery:",
        result.to_dict(),
    )

    if not result.valid:
        raise SystemExit(1)


if __name__ == "__main__":
    main()