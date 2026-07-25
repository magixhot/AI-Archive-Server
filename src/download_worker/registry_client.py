from src.model_registry.service import update_status
from src.model_registry.states import ModelStatus


def update_model_status(
    model_id: str,
    status: ModelStatus,
):
    update_status(
        model_id,
        status,
    )


def get_queued_models():
    from src.model_registry.service import get_models

    models = get_models()

    return [
        model
        for model in models
        if model[4] == ModelStatus.QUEUED.value
    ]