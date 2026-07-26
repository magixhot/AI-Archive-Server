from pathlib import Path

from .layout import create_model_layout
from .repository import copy_repository
from .cleanup import remove_repository_cache
from .file_index import generate_file_index
from .metadata import write_model_metadata
from .manifest import create_manifest
from .validator import validate_archive

from .registry import (
    create_registry,
    register_model
)


def build_archive(
    archive_root,
    model_id,
    source_repository,
    model_info
):

    family, model_name = model_id.split("/")


    # 1. Create structure

    model_path = create_model_layout(
        archive_root,
        family,
        model_name
    )

    repository_path = (
        model_path
        / "repository"
    )

    metadata_path = (
        model_path
        / "metadata"
    )


    # 2. Copy model repository

    copy_repository(
        source_repository,
        repository_path
    )


    # 3. Remove HF cache

    remove_repository_cache(
        repository_path
    )


    # 4. Generate files.json

    generate_file_index(
        repository_path,
        metadata_path / "files.json"
    )


    # 5. Write model metadata

    write_model_metadata(
        model_path,
        model_info
    )


    # 6. Create manifest

    create_manifest(
        model_path,
        model_id,
        family
    )


    # 7. Validate

    validation = validate_archive(
        model_path
    )


    if all(validation.values()):

        print("Registering model...")


        create_registry(
            "AI-Archive/registry/models.json"
        )


        register_model(
            "AI-Archive/registry/models.json",
            model_id,
            f"models/{family}/{model_name}",
            family
        )


    return {
        "path": str(model_path),
        "validation": validation
    }