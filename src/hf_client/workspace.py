from pathlib import Path


def workspace_path(model_id: str, destination: str) -> Path:
    """
    Compute the transient download workspace path for a model.

    Derives workspace identity from the full Hugging Face model_id
    so different namespaces cannot collide. The same model_id always
    maps to the same workspace path, preserving retry/resume semantics.

    Rejects unsafe or malformed model IDs that could escape the
    destination workspace.

    Args:
        model_id: Hugging Face model identifier (e.g. "owner/repo").
        destination: Base directory for transient workspaces.

    Returns:
        Path to the workspace directory.

    Raises:
        ValueError: If model_id is empty, contains path traversal,
                    or is otherwise unsafe.
    """
    if not model_id:
        raise ValueError("model_id must not be empty")

    if ".." in model_id:
        raise ValueError(f"model_id contains path traversal: {model_id}")

    if "/" in model_id:
        workspace_name = model_id.replace("/", "--")
    else:
        workspace_name = model_id

    workspace = Path(destination) / workspace_name
    return workspace
