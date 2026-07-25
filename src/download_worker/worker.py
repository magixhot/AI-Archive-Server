import time

from .registry_client import (
    get_queued_models,
    update_model_status,
)


def process_queue():

    print(
        "Download Worker started"
    )

    while True:

        models = get_queued_models()

        for model in models:

            model_id = model[0]

            print(
                f"Processing model: {model_id}"
            )

            update_model_status(
                model_id,
                "DOWNLOADING",
            )

        time.sleep(30)