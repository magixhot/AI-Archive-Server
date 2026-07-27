from pathlib import Path
import json
from datetime import datetime, timezone

from .result import IntegrityResult


HISTORY_ROOT = Path(
    "AI-Archive"
) / "integrity" / "history"



def save_history(
    result: IntegrityResult,
) -> Path:
    """
    Save integrity verification result.

    Returns:
        Path to created history file.
    """

    model_name = (
        result.model.replace(
            "/",
            "_",
        )
    )

    model_history = (
        HISTORY_ROOT
        / model_name
    )

    model_history.mkdir(
        parents=True,
        exist_ok=True,
    )


    timestamp = datetime.now(
        timezone.utc
    )


    filename = (
        timestamp
        .strftime(
            "%Y%m%d_%H%M%S"
        )
        + ".json"
    )


    output = {
        "model": result.model,
        "valid": result.valid,
        "checked_files": result.checked_files,
        "failed_files": result.failed_files,
        "timestamp": timestamp.isoformat(),
    }


    history_file = (
        model_history
        / filename
    )


    with open(
        history_file,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
        )


    return history_file