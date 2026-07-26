from . import registry


def _convert_model(row):
    """
    Convert registry database row
    into archive query format.
    """

    return {
        "id": row[1],
        "family": row[2],
        "path": None,
        "status": row[4],
    }


def _load_models():

    from model_registry.service import get_models

    rows = get_models()

    return [
        _convert_model(row)
        for row in rows
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