from src.storage.manager import create_storage
from src.model_registry.service import update_status
from src.model_registry.states import ModelStatus



def create_model_directory(
    model_id: str,
    family: str,
    version: str,
):

    model_name = model_id.split("/")[-1]


    update_status(
        model_id,
        ModelStatus.ARCHIVING,
    )


    return create_storage(
        family,
        model_name,
    )