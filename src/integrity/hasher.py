from hashlib import sha256
from pathlib import Path


def file_sha256(path: str | Path) -> str:

    path = Path(path)

    digest = sha256()

    with path.open("rb") as file:

        while True:

            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()