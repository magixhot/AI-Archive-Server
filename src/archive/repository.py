from pathlib import Path
import shutil


def copy_repository(
    source,
    destination
):

    source = Path(source)
    destination = Path(destination)

    if not source.exists():
        raise FileNotFoundError(
            f"Source repository not found: {source}"
        )

    destination.mkdir(
        parents=True,
        exist_ok=True
    )


    for item in source.iterdir():

        target = destination / item.name


        if item.is_dir():

            shutil.copytree(
                item,
                target,
                dirs_exist_ok=True
            )

        else:

            shutil.copy2(
                item,
                target
            )


    return destination