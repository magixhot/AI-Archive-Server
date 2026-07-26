from pathlib import Path


def validate_structure(
    model_path: Path,
) -> dict:

    checks = {

        "exists": model_path.exists(),

        "manifest": (
            model_path
            / "manifest.json"
        ).exists(),

        "metadata": (
            model_path
            / "metadata"
        ).exists(),

        "repository": (
            model_path
            / "repository"
        ).exists(),

    }


    return checks



def is_valid(
    checks: dict,
) -> bool:

    return all(
        checks.values()
    )