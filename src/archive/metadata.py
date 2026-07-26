import json
import hashlib
from pathlib import Path
from datetime import datetime



def write_json(path, data):

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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



def calculate_directory_size(
    directory
):

    directory = Path(directory)

    total = 0

    for file in directory.rglob("*"):

        if file.is_file():

            total += file.stat().st_size

    return total



def calculate_sha256(
    directory
):

    directory = Path(directory)

    sha256 = hashlib.sha256()


    for file in sorted(
        directory.rglob("*")
    ):

        if file.is_file():

            with open(
                file,
                "rb"
            ) as f:

                for chunk in iter(
                    lambda: f.read(1024 * 1024),
                    b""
                ):

                    sha256.update(
                        chunk
                    )


    return sha256.hexdigest()



def generate_model_metadata(
    model_path,
    model_id,
    family,
    version=None,
):

    model_path = Path(model_path)

    repository = (
        model_path
        / "repository"
    )


    metadata = {

        "model_id": model_id,

        "family": family,

        "version": version,

        "size_bytes":
            calculate_directory_size(
                repository
            ),

        "sha256":
            calculate_sha256(
                repository
            ),

        "created_at":
            datetime.utcnow()
            .isoformat()

    }


    write_model_metadata(
        model_path,
        metadata
    )


    return metadata



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