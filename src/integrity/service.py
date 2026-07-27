from pathlib import Path

from .validator import verify_manifest
from .result import IntegrityResult


def check_integrity(model_path: str | Path) -> IntegrityResult:
    """
    Run integrity check for model archive.

    Returns:
        IntegrityResult
    """

    path = Path(
        model_path
    )

    if not path.exists():

        return IntegrityResult(
            valid=False,
            model=path.name,
            checked_files=0,
            failed_files=[
                str(path)
            ]
        )


    result = verify_manifest(
        path
    )


    return IntegrityResult(
        valid=result["valid"],
        model=path.name,
        checked_files=result["checked_files"],
        failed_files=result["failed_files"]
    )