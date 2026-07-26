import json
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

ARCHIVE_ROOT = (
    BASE_DIR
    / "data"
    / "models"
)


def create_model_directory(
    model_id: str,
    family: str,
    version: str,
) -> Path:

    model_name = model_id.split("/")[-1]

    model_path = (
        ARCHIVE_ROOT
        / family
        / model_name
    )

    model_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    manifest = {

        "model_id": model_id,

        "family": family,

        "version": version,

        "status": "DOWNLOADING",

        "created_at": datetime.utcnow().isoformat()

    }

    with open(
        model_path / "manifest.json",
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            manifest,
            file,
            indent=4,
        )

    return model_path