import json
from pathlib import Path
from datetime import datetime


def create_manifest(
    model_path,
    model_id,
    family
):

    manifest = {
        "archive_version": "1.0",
        "model_id": model_id,
        "family": family,
        "created": datetime.utcnow().isoformat(),
        "storage": {
            "repository": "repository/",
            "metadata": "metadata/"
        }
    }

    path = (
        Path(model_path)
        / "manifest.json"
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            manifest,
            file,
            indent=2,
            ensure_ascii=False
        )

    return path