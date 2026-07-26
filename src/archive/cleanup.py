from pathlib import Path
import shutil
import os
import stat


def remove_readonly(func, path, exc_info):

    os.chmod(
        path,
        stat.S_IWRITE
    )

    func(path)


def remove_repository_cache(
    repository_path
):

    repository_path = Path(repository_path)

    cache_path = (
        repository_path
        / ".cache"
    )

    if cache_path.exists():

        shutil.rmtree(
            cache_path,
            onexc=remove_readonly
        )

        return True

    return False