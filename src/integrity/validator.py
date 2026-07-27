from pathlib import Path
import json

from .hasher import file_sha256


def validate_manifest(model_path: str | Path) -> bool:
    """
    Проверяет целостность архива.

    Возвращает True,
    если все файлы совпадают.
    """

    result = verify_manifest(
        model_path
    )

    return result["valid"]



def verify_manifest(model_path: str | Path) -> dict:
    """
    Проверяет файлы модели
    по metadata/files.json.
    """

    model_path = Path(
        model_path
    )

    files_index = (
        model_path
        / "metadata"
        / "files.json"
    )

    repository = (
        model_path
        / "repository"
    )


    if not files_index.exists():

        return {
            "valid": False,
            "checked_files": 0,
            "failed_files": [
                "files.json missing"
            ],
        }


    if not repository.exists():

        return {
            "valid": False,
            "checked_files": 0,
            "failed_files": [
                "repository missing"
            ],
        }


    with open(
        files_index,
        "r",
        encoding="utf-8",
    ) as file:

        files = json.load(
            file
        )


    failed_files = []

    checked_files = 0


    for item in files:

        relative_path = Path(
            item["path"]
        )

        target = (
            repository
            / relative_path
        )

        checked_files += 1


        if not target.exists():

            failed_files.append(
                item["path"]
            )

            continue


        current_hash = file_sha256(
            target
        )


        if current_hash != item["sha256"]:

            failed_files.append(
                item["path"]
            )


    return {
        "valid": len(failed_files) == 0,
        "checked_files": checked_files,
        "failed_files": failed_files,
    }