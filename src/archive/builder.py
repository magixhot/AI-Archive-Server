from pathlib import Path

from storage.manager import (
    create_storage,
)

from storage.validator import (
    validate_structure,
    is_valid,
)

from model_registry.service import (
    update_status,
)

from model_registry.states import (
    ModelStatus,
)


from .repository import copy_repository
from .cleanup import remove_repository_cache
from .file_index import generate_file_index
from .metadata import generate_model_metadata
from .manifest import create_manifest



def build_archive(
    model_id,
    source_repository,
    model_info,
):

    family, model_name = model_id.split("/")


    #
    # ARCHIVING START
    #

    update_status(
        model_id,
        ModelStatus.ARCHIVING,
    )


    try:

        #
        # Create storage structure
        #

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


        #
        # Copy repository
        #

        copy_repository(
            source_repository,
            repository_path,
        )


        #
        # Remove HF cache
        #

        remove_repository_cache(
            repository_path,
        )


        #
        # Generate index
        #

        generate_file_index(
            repository_path,
            metadata_path
            / "files.json",
        )


        #
        # Generate metadata
        #

        metadata = generate_model_metadata(
            model_path,
            model_id,
            family,
            model_info.get(
                "version"
            ),
        )


        #
        # Manifest
        #

        create_manifest(
            model_path,
            model_id,
            family,
            model_info.get(
                "version"
            ),
        )


        #
        # ARCHIVED
        #

        update_status(
            model_id,
            ModelStatus.ARCHIVED,
        )


        #
        # VALIDATION
        #

        update_status(
            model_id,
            ModelStatus.VALIDATING,
        )


        checks = validate_structure(
            model_path,
        )


        if not is_valid(
            checks
        ):

            update_status(
                model_id,
                ModelStatus.FAILED,
            )

            return {

                "path": str(model_path),

                "validation": checks,

                "status": "FAILED",

            }


        #
        # VALIDATED
        #

        update_status(
            model_id,
            ModelStatus.VALIDATED,
        )


        #
        # READY
        #

        update_status(
            model_id,
            ModelStatus.READY,
        )


        return {

            "path": str(model_path),

            "validation": checks,

            "metadata": metadata,

            "status": "READY",

        }


    except Exception:


        update_status(
            model_id,
            ModelStatus.FAILED,
        )


        raise