import json
from pathlib import Path


def load_registry(registry_path):

    registry_path = Path(
        registry_path
    )

    with open(
        registry_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)



def list_models(registry_path):

    registry = load_registry(
        registry_path
    )

    return registry.get(
        "models",
        []
    )

def count_models(
    registry_path
):

    models = list_models(
        registry_path
    )

    return len(models)



def list_families(
    registry_path
):

    models = list_models(
        registry_path
    )

    families = set()

    for model in models:

        families.add(
            model["family"]
        )

    return sorted(
        families
    )



def find_by_family(
    registry_path,
    family
):

    models = list_models(
        registry_path
    )

    result = []

    for model in models:

        if model["family"] == family:

            result.append(
                model
            )

    return result

def get_model(
    registry_path,
    model_id
):

    models = list_models(
        registry_path
    )

    for model in models:

        if model["id"] == model_id:

            return model


    return None