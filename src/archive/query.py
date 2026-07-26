def _convert_model(model):
    """
    Convert registry model record
    into archive query format.
    """

    return {
        "id": model["model_id"],
        "family": model["family"],
        "version": model["version"],
        "path": model["storage_path"],
        "size_bytes": model["size_bytes"],
        "sha256": model["sha256"],
        "status": model["status"],
    }



def _load_models():

    from model_registry.service import get_all_models

    models = get_all_models()

    return [
        _convert_model(model)
        for model in models
    ]



def list_models():

    return _load_models()



def count_models():

    models = list_models()

    return len(models)



def list_families():

    models = list_models()

    families = set()

    for model in models:

        if model["family"]:

            families.add(
                model["family"]
            )

    return sorted(
        families
    )



def find_by_family(
    family
):

    models = list_models()

    result = []

    for model in models:

        if model["family"] == family:

            result.append(
                model
            )

    return result



def get_model(
    model_id
):

    models = list_models()

    for model in models:

        if model["id"] == model_id:

            return model

    return None