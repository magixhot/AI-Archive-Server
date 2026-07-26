from pathlib import Path
import shutil

from .paths import get_model_path


def create_storage(
    family: str,
    model_name: str,
) -> Path:

    model_path = get_model_path(
        family,
        model_name,
    )

    model_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return model_path



def storage_exists(
    family: str,
    model_name: str,
) -> bool:

    model_path = get_model_path(
        family,
        model_name,
    )

    return model_path.exists()



def get_storage_size(
    family: str,
    model_name: str,
) -> int:

    model_path = get_model_path(
        family,
        model_name,
    )

    if not model_path.exists():
        return 0


    total_size = 0

    for file in model_path.rglob("*"):

        if file.is_file():

            total_size += file.stat().st_size


    return total_size


def remove_storage(
    family: str,
    model_name: str,
) -> None:

    model_path = get_model_path(
        family,
        model_name,
    )

    if model_path.exists():

        shutil.rmtree(
            model_path
        )


    family_path = model_path.parent


    if family_path.exists() and not any(
        family_path.iterdir()
    ):

        family_path.rmdir()