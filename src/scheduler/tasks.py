from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TaskResult:
    task_name: str
    success: bool
    message: str
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "task_name": self.task_name,
            "success": self.success,
            "message": self.message,
            "details": self.details,
        }


def run_integrity_check(
    models_root: str | Path,
) -> TaskResult:
    from src.integrity.service import check_integrity

    models_path = Path(models_root)

    if not models_path.exists():
        return TaskResult(
            task_name="integrity_check",
            success=False,
            message=f"Models root does not exist: {models_path}",
        )

    results: list[dict] = []
    errors: list[str] = []

    for model_dir in sorted(models_path.iterdir()):
        if not model_dir.is_dir():
            continue

        for family_dir in sorted(model_dir.iterdir()):
            if not family_dir.is_dir():
                continue

            model_path = family_dir

            try:
                result = check_integrity(model_path)
                results.append({
                    "model": result.model,
                    "valid": result.valid,
                    "checked_files": result.checked_files,
                    "failed_files": result.failed_files,
                })

                if not result.valid:
                    logger.warning(
                        "Integrity check failed: %s",
                        result.model,
                    )
            except Exception as exc:
                error_msg = f"{model_path}: {exc}"
                errors.append(error_msg)
                logger.error(
                    "Integrity check error: %s",
                    error_msg,
                )

    total = len(results)
    passed = sum(1 for r in results if r["valid"])
    failed = total - passed

    return TaskResult(
        task_name="integrity_check",
        success=not errors,
        message=(
            f"Checked {total} models: "
            f"{passed} passed, {failed} failed, "
            f"{len(errors)} errors"
        ),
        details={
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
        },
    )


def run_reconciliation(
    archive_root: str | Path,
) -> TaskResult:
    from src.reconciliation.service import reconcile_archive

    archive_path = Path(archive_root)

    if not archive_path.exists():
        return TaskResult(
            task_name="reconciliation",
            success=False,
            message=f"Archive root does not exist: {archive_path}",
        )

    try:
        result = reconcile_archive(archive_path)

        return TaskResult(
            task_name="reconciliation",
            success=result.valid,
            message=(
                f"Reconciled {len(result.reconciled)} models, "
                f"skipped {len(result.skipped)}, "
                f"errors {len(result.errors)}"
            ),
            details=result.to_dict(),
        )
    except Exception as exc:
        return TaskResult(
            task_name="reconciliation",
            success=False,
            message=f"Reconciliation failed: {exc}",
        )


def run_archive_sync(
    source_root: str | Path,
    target_root: str | Path,
    *,
    dry_run: bool = True,
) -> TaskResult:
    from src.archive_sync.service import sync_archive

    source_path = Path(source_root)
    target_path = Path(target_root)

    if not source_path.exists():
        return TaskResult(
            task_name="archive_sync",
            success=False,
            message=f"Source archive does not exist: {source_path}",
        )

    try:
        result = sync_archive(
            source_path,
            target_path,
            dry_run=dry_run,
        )

        return TaskResult(
            task_name="archive_sync",
            success=result.valid,
            message=(
                f"Sync ({'dry-run' if dry_run else 'live'}): "
                f"copied {len(result.copied_files)}, "
                f"unchanged {len(result.unchanged_files)}, "
                f"errors {len(result.errors)}"
            ),
            details=result.to_dict(),
        )
    except Exception as exc:
        return TaskResult(
            task_name="archive_sync",
            success=False,
            message=f"Archive sync failed: {exc}",
        )
