from pathlib import Path

from .validator import verify_manifest
from .result import IntegrityResult
from .history import save_history


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

        result = IntegrityResult(
            valid=False,
            model=path.name,
            checked_files=0,
            failed_files=[
                str(path)
            ]
        )

        save_history(
            result
        )

        return result


    verification = verify_manifest(
        path
    )


    result = IntegrityResult(
        valid=verification["valid"],
        model=path.name,
        checked_files=verification["checked_files"],
        failed_files=verification["failed_files"]
    )


    save_history(
        result
    )


    return result