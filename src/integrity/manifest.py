from pathlib import Path
import json

from .hasher import file_sha256


IGNORE_DIRS = {
    ".cache",
    ".git",
    "__pycache__",
}

IGNORE_FILES = {
    "manifest.json",
}


def build_manifest(model_path: str | Path):

    model_path = Path(model_path)

    manifest = []

    for file in sorted(model_path.rglob("*")):

        if not file.is_file():
            continue

        relative = file.relative_to(model_path)

        # Пропускаем служебные каталоги
        if (
            relative.parts
            and relative.parts[0] in IGNORE_DIRS
        ):
            continue

        # Пропускаем сам manifest.json
        if file.name in IGNORE_FILES:
            continue

        manifest.append(
            {
                "path": relative.as_posix(),
                "size": file.stat().st_size,
                "sha256": file_sha256(file),
            }
        )

    return manifest


def write_manifest(model_path: str | Path):

    model_path = Path(model_path)

    manifest = build_manifest(model_path)

    output = {
        "files": manifest
    }

    with open(
        model_path / "manifest.json",
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
        )

    return model_path / "manifest.json"