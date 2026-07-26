import json
from pathlib import Path


def write_json(path, data):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


def write_model_metadata(
    model_path,
    model_info
):

    path = (
        Path(model_path)
        / "metadata"
        / "model.json"
    )

    write_json(
        path,
        model_info
    )


def write_files_metadata(
    model_path,
    files
):

    path = (
        Path(model_path)
        / "metadata"
        / "files.json"
    )

    write_json(
        path,
        files
    )