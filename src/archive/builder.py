from src.model_registry.api import register_model

from .layout import create_model_layout
from .repository import copy_repository
from .cleanup import remove_repository_cache
from .file_index import generate_file_index
from .metadata import generate_model_metadata
from .manifest import create_manifest
from .validator import validate_archive



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


    # 4. Generate files index

    generate_file_index(
        repository_path,
        metadata_path / "files.json"
    )


    # 5. Generate model metadata

    metadata = generate_model_metadata(
        model_path,
        model_id,
        family,
        model_info.get(
            "version"
        )
    )


    # 6. Create manifest

    create_manifest(
    model_path,
    model_id,
    family,
    model_info.get(
        "version"
    )
)


    # 7. Validate archive

    validation = validate_archive(
        model_path
    )


    if all(validation.values()):

        print(
            "Registering model in SQLite Registry..."
        )


        register_model(

            model_id=model_id,

            family=family,

            version=model_info.get(
                "version"
            ),

            storage_path=str(
                model_path
            ),

            size_bytes=metadata[
                "size_bytes"
            ],

            sha256=metadata[
                "sha256"
            ],
        )


    return {

        "path": str(
            model_path
        ),

        "validation": validation,

        "metadata": metadata,

    }