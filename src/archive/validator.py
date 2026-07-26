from pathlib import Path
import json
import hashlib



def calculate_sha256(
    file_path,
    chunk_size=1024 * 1024,
):

    sha256 = hashlib.sha256()


    with open(
        file_path,
        "rb",
    ) as file:

        while True:

            chunk = file.read(
                chunk_size
            )

            if not chunk:

                break

            sha256.update(
                chunk
            )


    return sha256.hexdigest()



def validate_file_integrity(
    repository,
    files,
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



        if "sha256" in item:

            actual_sha256 = calculate_sha256(
                file_path
            )


            if actual_sha256 != item["sha256"]:

                return False



    return True



def validate_manifest(
    manifest_path,
):

    if not manifest_path.exists():

        return False


    try:

        with open(
            manifest_path,
            "r",
            encoding="utf-8",
        ) as file:

            manifest = json.load(file)


    except Exception:

        return False



    required = [

        "archive_version",

        "model_id",

        "family",

        "status",

        "storage",

        "metadata",

    ]


    for field in required:

        if field not in manifest:

            return False



    return True



def validate_archive(
    archive_path,
):

    archive_path = Path(
        archive_path
    )


    result = {

        "manifest": False,

        "metadata": False,

        "repository": False,

        "files": False,

    }



    manifest = (
        archive_path
        / "manifest.json"
    )


    result["manifest"] = validate_manifest(
        manifest
    )



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

        try:

            with open(
                files_json,
                "r",
                encoding="utf-8",
            ) as file:

                files = json.load(file)


            result["files"] = validate_file_integrity(
                repository,
                files,
            )


        except Exception:

            result["files"] = False



    return result