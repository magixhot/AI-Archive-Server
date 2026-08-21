from huggingface_hub import snapshot_download

from src.hf_client.workspace import workspace_path


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

    download_path = workspace_path(model_id, destination)

    download_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = snapshot_download(
        repo_id=model_id,
        local_dir=str(download_path),
    )

    return path