from pathlib import Path
import json
from datetime import datetime


def create_registry(
    registry_path
):

    registry_path = Path(
        registry_path
    )


    registry_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    if not registry_path.exists():

        data = {
            "version": "1.0",
            "created": datetime.utcnow().isoformat(),
            "models": []
        }


        with open(
            registry_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False
            )


    return registry_path



def register_model(
    registry_path,
    model_id,
    model_path,
    family,
    status="active"
):

    registry_path = Path(
        registry_path
    )


    with open(
        registry_path,
        "r",
        encoding="utf-8"
    ) as file:

        registry = json.load(file)


    model = {

        "id": model_id,

        "family": family,

        "path": model_path,

        "status": status
    }


    registry["models"].append(
        model
    )


    with open(
        registry_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            registry,
            file,
            indent=2,
            ensure_ascii=False
        )


    return model