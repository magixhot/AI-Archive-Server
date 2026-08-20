from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


IGNORED_MODEL_DIRECTORIES = {
    "Checksums",
    "Documentation",
    "GGUF",
    "Safetensors",
}


@dataclass(frozen=True)
class DiscoveredModel:
    family: str
    model_name: str
    model_root: Path
    repository_path: Path


def has_model_weights(
    repository_path: Path,
) -> bool:
    index_file = (
        repository_path
        / "model.safetensors.index.json"
    )

    if index_file.is_file():
        return True

    return any(
        repository_path.glob(
            "*.safetensors"
        )
    )


def is_model_root(
    model_root: Path,
) -> bool:
    if not model_root.is_dir():
        return False

    if model_root.name in IGNORED_MODEL_DIRECTORIES:
        return False

    repository_path = (
        model_root
        / "Repository"
    )

    if not repository_path.is_dir():
        return False

    config_path = (
        repository_path
        / "config.json"
    )

    if not config_path.is_file():
        return False

    if not has_model_weights(
        repository_path
    ):
        return False

    return True


def discover_models(
    archive_root: str | Path,
) -> list[DiscoveredModel]:
    archive_root = Path(
        archive_root
    ).resolve()

    discovered: list[
        DiscoveredModel
    ] = []

    if not archive_root.is_dir():
        return discovered

    for family_path in sorted(
        archive_root.iterdir()
    ):
        if not family_path.is_dir():
            continue

        family = family_path.name

        for model_root in sorted(
            family_path.iterdir()
        ):
            if not is_model_root(
                model_root
            ):
                continue

            discovered.append(
                DiscoveredModel(
                    family=family,
                    model_name=model_root.name,
                    model_root=model_root,
                    repository_path=(
                        model_root
                        / "Repository"
                    ),
                )
            )

    return discovered