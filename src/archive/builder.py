from src.storage.manager import create_storage

from src.model_registry.service import (
    update_model_metadata,
    update_status,
)

from src.model_registry.states import ModelStatus

from .repository import copy_repository
from .cleanup import remove_repository_cache
from .file_index import generate_file_index
from .metadata import generate_model_metadata
from .manifest import create_manifest
from .validator import validate_archive


def build_archive(
    model_id,
    source_repository,
    model_info,
):

    family, model_name = model_id.split("/", 1)

    update_status(
        model_id,
        ModelStatus.ARCHIVING,
    )

    model_path = create_storage(
        family,
        model_name,
    )

    repository_path = (
        model_path
        / "repository"
    )

    metadata_path = (
        model_path
        / "metadata"
    )

    copy_repository(
        source_repository,
        repository_path,
    )

    remove_repository_cache(
        repository_path,
    )

    generate_file_index(
        repository_path,
        metadata_path / "files.json",
    )

    metadata = generate_model_metadata(
        model_path,
        model_id,
        family,
        model_info.get(
            "version"
        ),
    )

    create_manifest(
        model_path,
        model_id,
        family,
        model_info.get(
            "version"
        ),
    )

    validation = validate_archive(
        model_path,
    )

    if validation["valid"]:

        update_model_metadata(
            model_id=model_id,
            storage_path=str(model_path),
            size_bytes=metadata["size_bytes"],
            sha256=metadata["sha256"],
        )

        update_status(
            model_id,
            ModelStatus.VALIDATED,
        )

    else:

        update_status(
            model_id,
            ModelStatus.FAILED,
        )

    return {
        "path": str(model_path),
        "validation": validation,
        "metadata": metadata,
    }
