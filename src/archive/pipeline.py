from pathlib import Path

from src.integrity.validator import verify_manifest
from src.integrity.result import IntegrityResult


def verify_archive(model_path: str) -> IntegrityResult:
    """
    Verify model archive integrity.

    Returns:
        IntegrityResult with verification status.
    """

    path = Path(model_path)

    if not path.exists():
        return IntegrityResult(
            valid=False,
            model=path.name,
            checked_files=0,
            failed_files=[
                str(path)
            ]
        )

    verification = verify_manifest(
        path
    )

    return IntegrityResult(
        valid=verification["valid"],
        model=path.name,
        checked_files=verification["checked_files"],
        failed_files=verification["failed_files"]
    )