from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from src.model_registry.models import ModelRecord
from src.model_registry.service import (
    add_model,
    mark_archive_created,
    model_exists,
    update_model_metadata,
)

from .discovery import discover_models
from .metadata import resolve_metadata


@dataclass
class ReconciliationResult:
    reconciled: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "reconciled": self.reconciled,
            "skipped": self.skipped,
            "errors": self.errors,
        }


def _repository_size(
    repository_path: Path,
) -> int:
    total_size = 0

    for path in repository_path.rglob("*"):
        if path.is_file():
            total_size += path.stat().st_size

    return total_size


def reconcile_archive(
    archive_root: str | Path,
    *,
    overrides: dict[str, str] | None = None,
) -> ReconciliationResult:
    result = ReconciliationResult()
    overrides = overrides or {}

    for model in discover_models(
        archive_root
    ):
        try:
            metadata = resolve_metadata(
                model,
                override_model_id=overrides.get(
                    model.model_name
                ),
            )

            if metadata is None:
                result.skipped.append(
                    f"{model.family}/{model.model_name}: "
                    "model_id unresolved"
                )
                continue

            size_bytes = _repository_size(
                model.repository_path
            )

            storage_path = str(
                model.model_root
            )

            if not model_exists(
                metadata.model_id
            ):
                add_model(
                    ModelRecord(
                        model_id=metadata.model_id,
                        family=metadata.family,
                        version=metadata.version,
                        storage_path=storage_path,
                    )
                )

            update_model_metadata(
                model_id=metadata.model_id,
                storage_path=storage_path,
                size_bytes=size_bytes,
                sha256=None,
            )

            mark_archive_created(
                metadata.model_id
            )

            result.reconciled.append(
                metadata.model_id
            )

        except Exception as error:
            result.errors.append(
                f"{model.family}/{model.model_name}: "
                f"{error}"
            )

    return result