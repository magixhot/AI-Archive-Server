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
        "rb"
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



def generate_file_index(
    repository_path,
    output_path,
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

                    "size": file.stat().st_size,

                    "sha256": calculate_sha256(
                        file
                    ),

                }

            )



    output_path = Path(
        output_path
    )


    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:


        json.dump(

            files,

            f,

            indent=2,

            ensure_ascii=False,

        )


    return files