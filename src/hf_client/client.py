from huggingface_hub import HfApi
from huggingface_hub import snapshot_download

from huggingface_hub import (
    HfApi,
    snapshot_download,
) 

from .models import (
    HFFile,
    HFModelInfo,
    HFRepository,
)


api = HfApi()


def model_exists(model_id: str) -> bool:

    try:
        api.model_info(model_id)
        return True

    except Exception:
        return False


def get_model_info(
    model_id: str,
) -> HFModelInfo:

    info = api.model_info(model_id)

    return HFModelInfo(
        model_id=model_id,
        author=info.author,
        sha=info.sha,
        private=info.private,
        disabled=info.disabled,
    )


def list_model_files(
    model_id: str,
) -> list[HFFile]:

    info = api.model_info(model_id)

    files = []

    for sibling in info.siblings:

        files.append(
            HFFile(
                path=sibling.rfilename,
                size=0,
            )
        )

    return files


def get_repository(
    model_id: str,
) -> HFRepository:

    return HFRepository(
        info=get_model_info(model_id),
        files=list_model_files(model_id),
    )
    
def download_model(
    model_id: str,
    destination: str,
) -> str:
    return snapshot_download(
        repo_id=model_id,
        local_dir=destination,
    )