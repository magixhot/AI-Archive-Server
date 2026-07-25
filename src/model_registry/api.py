from .models import ModelRecord
from .service import add_model


def register_model(
    model_id: str,
    family: str | None = None,
    version: str | None = None,
):

    model = ModelRecord(
        model_id=model_id,
        family=family,
        version=version,
    )

    add_model(model)

    return {
        "model_id": model.model_id,
        "status": model.status,
    }