from pathlib import Path
import json


def generate_file_index(
    repository_path,
    output_path
):

    repository_path = Path(
        repository_path
    )

    files = []


    for file in repository_path.rglob("*"):

        if file.is_file():

            relative_path = (
                file.relative_to(
                    repository_path
                )
            )


            files.append(
                {
                    "path": str(relative_path),
                    "size": file.stat().st_size
                }
            )


    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            files,
            f,
            indent=2,
            ensure_ascii=False
        )


    return files