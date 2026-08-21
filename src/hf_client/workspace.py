from pathlib import Path
import re


def workspace_path(model_id: str, destination: str) -> Path:
    """
    Compute the transient download workspace path for a model.

    Derives workspace identity from the full Hugging Face model_id
    so different namespaces cannot collide. The same model_id always
    maps to the same workspace path, preserving retry/resume semantics.

    Rejects unsafe or malformed model IDs that could escape the
    destination workspace.

    Enforces canonical Hugging Face repository identity as exactly
    ``namespace/repository`` (two non-empty path segments).

    Args:
        model_id: Hugging Face model identifier (e.g. "owner/repo").
        destination: Base directory for transient workspaces.

    Returns:
        Path to the workspace directory.

    Raises:
        ValueError: If model_id is empty, contains path traversal,
                    has structural anomalies, or is otherwise unsafe.
    """
    if not model_id:
        raise ValueError("model_id must not be empty")

    if ".." in model_id:
        raise ValueError(f"model_id contains path traversal: {model_id}")

    if model_id.startswith("/") or model_id.endswith("/"):
        raise ValueError(
            f"model_id has leading or trailing slash: {model_id}"
        )

    if "\\" in model_id:
        raise ValueError(f"model_id contains backslash: {model_id}")

    if "//" in model_id:
        raise ValueError(f"model_id contains repeated slash: {model_id}")

    if "/" not in model_id:
        raise ValueError(
            f"model_id must contain namespace/repository format: {model_id}"
        )

    parts = model_id.split("/")
    if len(parts) != 2:
        raise ValueError(
            f"model_id must have exactly two path segments: {model_id}"
        )

    namespace, repository = parts

    if not namespace:
        raise ValueError(f"model_id has empty namespace: {model_id}")

    if not repository:
        raise ValueError(f"model_id has empty repository: {model_id}")

    if namespace == "." or repository == ".":
        raise ValueError(f"model_id contains '.' segment: {model_id}")

    if not re.match(r"^[A-Za-z0-9._-]+$", namespace):
        raise ValueError(
            f"model_id namespace contains invalid characters: {model_id}"
        )

    if not re.match(r"^[A-Za-z0-9._-]+$", repository):
        raise ValueError(
            f"model_id repository contains invalid characters: {model_id}"
        )

    workspace = Path(destination) / namespace / repository
    return workspace
