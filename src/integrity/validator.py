from pathlib import Path
import json

from .manifest import build_manifest


def validate_manifest(model_path: str | Path) -> bool:
    """
    Проверяет соответствие файлов manifest.json.

    Возвращает True, если всё совпадает.
    """

    result = verify_manifest(
        model_path
    )

    return result["valid"]


def verify_manifest(model_path: str | Path) -> dict:
    """
    Выполняет проверку manifest.json
    и возвращает подробный результат.
    """

    model_path = Path(model_path)

    manifest_file = model_path / "manifest.json"

    if not manifest_file.exists():
        return {
            "valid": False,
            "checked_files": 0,
            "failed_files": [
                "manifest.json missing"
            ]
        }

    with open(
        manifest_file,
        "r",
        encoding="utf-8",
    ) as file:

        stored = json.load(file)["files"]

    current = build_manifest(
        model_path
    )

    checked_files = len(stored)

    failed_files = []

    if stored != current:
        failed_files.append(
            "manifest mismatch"
        )

    return {
        "valid": stored == current,
        "checked_files": checked_files,
        "failed_files": failed_files,
    }