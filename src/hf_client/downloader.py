from pathlib import Path

from huggingface_hub import snapshot_download


def download_repository(
    model_id: str,
    destination: str,
):
    """
    Download an entire Hugging Face repository.

    Each model is downloaded into its own temporary
    workspace under the destination directory.

    Returns the local path where the repository
    was downloaded.
    """

    model_name = model_id.split("/")[-1]

    download_path = (
        Path(destination)
        / model_name
    )

    download_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = snapshot_download(
        repo_id=model_id,
        local_dir=str(download_path),
    )

    return path