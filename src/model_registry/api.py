from .models import ModelRecord

from .service import (
    add_model,
    get_all_models,
    get_model,
    get_families,
    model_exists,
)



def register_model(
    model_id: str,
    family: str | None = None,
    version: str | None = None,
    storage_path: str | None = None,
    size_bytes: int | None = None,
    sha256: str | None = None,
):

    if model_exists(
        model_id
    ):
        existing = get_model(
            model_id
        )

        return {
            "model_id": model_id,
            "status": existing["status"],
            "existing": True,
        }

    model = ModelRecord(

        model_id=model_id,

        family=family,

        version=version,

        storage_path=storage_path,

        size_bytes=size_bytes,

        sha256=sha256,
    )


    add_model(
        model
    )


    return {

        "model_id": model.model_id,

        "status": model.status,

        "existing": False,

    }



def list_models():

    return get_all_models()



def find_model(
    model_id: str,
):

    return get_model(
        model_id
    )



def list_families():

    return get_families()