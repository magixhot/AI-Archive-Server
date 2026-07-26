from pathlib import Path


def create_model_layout(
    archive_root: str,
    family: str,
    model_name: str
):
    model_path = (
        Path(archive_root)
        / "models"
        / family
        / model_name
    )

    for directory in [
        model_path,
        model_path / "metadata",
        model_path / "repository",
    ]:
        directory.mkdir(
            parents=True,
            exist_ok=True
        )

    return model_path