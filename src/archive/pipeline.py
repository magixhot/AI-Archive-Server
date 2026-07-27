from pathlib import Path

from src.integrity.validator import validate_manifest


def verify_archive(model_path: str) -> bool:
    """
    Verify model archive integrity.

    Returns:
        True  - archive is valid
        False - archive is corrupted
    """

    path = Path(model_path)

    if not path.exists():
        return False

    return validate_manifest(
        path
    )