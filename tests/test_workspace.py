import pytest
from pathlib import Path

from src.hf_client.workspace import workspace_path


def test_owner_collision_different_paths():
    """owner-a/shared-model and owner-b/shared-model map to different paths."""
    dest = "/tmp/test_downloads"
    path_a = workspace_path("owner-a/shared-model", dest)
    path_b = workspace_path("owner-b/shared-model", dest)
    assert path_a != path_b
    assert "owner-a--shared-model" in str(path_a)
    assert "owner-b--shared-model" in str(path_b)


def test_deterministic_mapping():
    """Same model_id maps deterministically to the same path."""
    dest = "/tmp/test_downloads"
    path1 = workspace_path("owner/repo", dest)
    path2 = workspace_path("owner/repo", dest)
    assert path1 == path2


def test_valid_normal_hf_ids():
    """Valid normal Hugging Face IDs work."""
    dest = "/tmp/test_downloads"
    
    # Standard owner/repo format
    path1 = workspace_path("Qwen/Qwen3-0.6B", dest)
    assert path1 == Path(dest) / "Qwen--Qwen3-0.6B"
    
    # Single name (no slash)
    path2 = workspace_path("model-name", dest)
    assert path2 == Path(dest) / "model-name"
    
    # Multiple slashes
    path3 = workspace_path("org/subgroup/model", dest)
    assert path3 == Path(dest) / "org--subgroup--model"


def test_traversal_rejected():
    """Traversal / malformed IDs are rejected."""
    dest = "/tmp/test_downloads"
    
    # Path traversal
    with pytest.raises(ValueError, match="path traversal"):
        workspace_path("../etc/passwd", dest)
    
    # Double traversal
    with pytest.raises(ValueError, match="path traversal"):
        workspace_path("owner/../../secret", dest)
    
    # Empty model_id
    with pytest.raises(ValueError, match="must not be empty"):
        workspace_path("", dest)


def test_destination_path_included():
    """Workspace path includes the destination directory."""
    dest = "/some/custom/destination"
    path = workspace_path("owner/repo", dest)
    assert str(path).startswith(dest)
