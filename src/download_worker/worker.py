import time

from .archive import create_model_directory
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
            family = model[2]
            version = model[3]
            
            print(
                f"Processing model: {model_id}"
            )

            update_model_status(
                model_id,
                ModelStatus.DOWNLOADING,
            )

            model_path = create_model_directory(
                model_id,
                family,
                version,
            )

            print(
                f"Archive created: {model_path}"
            )

            time.sleep(2)

            update_model_status(
                model_id,
                ModelStatus.DOWNLOADED,
            )

            print(
                f"Finished: {model_id}"
            )