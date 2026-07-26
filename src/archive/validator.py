from pathlib import Path
import json


def validate_file_sizes(
    repository,
    files
):

    for item in files:

        file_path = (
            repository
            / item["path"]
        )

        if not file_path.exists():

            return False


        actual_size = (
            file_path.stat()
            .st_size
        )


        expected_size = (
            item["size"]
        )


        if actual_size != expected_size:

            return False


    return True



def validate_archive(
    archive_path
):

    archive_path = Path(
        archive_path
    )

    result = {
        "manifest": False,
        "metadata": False,
        "repository": False,
        "files": False
    }


    manifest = (
        archive_path
        / "manifest.json"
    )

    if manifest.exists():

        result["manifest"] = True



    metadata_path = (
        archive_path
        / "metadata"
    )

    model_json = (
        metadata_path
        / "model.json"
    )

    files_json = (
        metadata_path
        / "files.json"
    )


    if (
        model_json.exists()
        and files_json.exists()
    ):

        result["metadata"] = True



    repository = (
        archive_path
        / "repository"
    )


    if (
        repository.exists()
        and any(repository.iterdir())
    ):

        result["repository"] = True



    if files_json.exists():

        with open(
            files_json,
            "r",
            encoding="utf-8"
        ) as file:

            files = json.load(file)


        result["files"] = validate_file_sizes(
            repository,
            files
        )


    return result