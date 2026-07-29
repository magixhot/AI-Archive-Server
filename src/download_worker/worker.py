import time

from src.hf_client.downloader import download_repository
from src.archive.builder import build_archive
from src.storage.cache import get_cached_archive

from .registry_client import (
    get_queued_models,
    update_model_status,
)

from src.model_registry.states import ModelStatus


def process_queue():

    while True:

        models = get_queued_models()

        if not models:
            time.sleep(5)
            continue

        for model in models:

            model_id = model[1]

            print(
                f"Processing model: {model_id}"
            )

            cached_archive = get_cached_archive(
                model_id
            )

            if cached_archive:

                print(
                    f"Using cached archive: {cached_archive}"
                )

                update_model_status(
                    model_id,
                    ModelStatus.VALIDATED,
                )

                continue

            update_model_status(
                model_id,
                ModelStatus.DOWNLOADING,
            )

            print(
                "Downloading model..."
            )

            source_repository = download_repository(
                model_id,
                "data/downloads",
            )

            print(
                f"Downloaded to: {source_repository}"
            )

            model_info = {
                "version": model[3],
            }

            print(
                "Building archive..."
            )

            result = build_archive(
                model_id,
                source_repository,
                model_info,
            )

            print(
                f"Archive created: {result['path']}"
            )

            print(
                f"Finished: {model_id}"
            )
