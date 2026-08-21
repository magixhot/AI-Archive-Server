import pytest
from pathlib import Path

from src.hf_client.workspace import workspace_path


def test_owner_collision_different_paths():
    """owner-a/shared-model and owner-b/shared-model map to different paths."""
    dest = "/tmp/test_downloads"
    path_a = workspace_path("owner-a/shared-model", dest)
    path_b = workspace_path("owner-b/shared-model", dest)
    assert path_a != path_b
    assert path_a == Path(dest) / "owner-a/shared-model"
    assert path_b == Path(dest) / "owner-b/shared-model"


def test_slash_vs_double_dash():
    """owner/repo != owner--repo (slash must not be flattened to double dash)."""
    dest = "/tmp/test_downloads"
    path_slash = workspace_path("owner/repo", dest)
    assert path_slash == Path(dest) / "owner/repo"

    with pytest.raises(ValueError, match="namespace/repository format"):
        workspace_path("owner--repo", dest)


def test_deterministic_mapping():
    """Same model_id maps deterministically to the same path."""
    dest = "/tmp/test_downloads"
    path1 = workspace_path("owner/repo", dest)
    path2 = workspace_path("owner/repo", dest)
    assert path1 == path2


def test_valid_normal_hf_ids():
    """Valid normal Hugging Face IDs work."""
    dest = "/tmp/test_downloads"

    path1 = workspace_path("Qwen/Qwen3-0.6B", dest)
    assert path1 == Path(dest) / "Qwen/Qwen3-0.6B"

    path2 = workspace_path("google/gemma-3-27b-it", dest)
    assert path2 == Path(dest) / "google/gemma-3-27b-it"

    path3 = workspace_path("moonshotai/Kimi-K2-Instruct", dest)
    assert path3 == Path(dest) / "moonshotai/Kimi-K2-Instruct"


def test_multi_level_namespace():
    """Multi-level namespace model IDs are preserved structurally."""
    dest = "/tmp/test_downloads"
    path = workspace_path("org/subgroup/model", dest)
    assert path == Path(dest) / "org/subgroup/model"


def test_traversal_rejected():
    """Traversal attempts are rejected."""
    dest = "/tmp/test_downloads"

    with pytest.raises(ValueError, match="path traversal"):
        workspace_path("../etc/passwd", dest)

    with pytest.raises(ValueError, match="path traversal"):
        workspace_path("owner/../../secret", dest)


def test_absolute_path_rejected():
    """Absolute-path-like inputs are rejected."""
    dest = "/tmp/test_downloads"

    with pytest.raises(ValueError, match="unsafe characters"):
        workspace_path("/etc/passwd", dest)


def test_backslash_rejected():
    """Backslash-based unsafe inputs are rejected."""
    dest = "/tmp/test_downloads"

    with pytest.raises(ValueError, match="unsafe characters"):
        workspace_path("owner\\repo", dest)

    with pytest.raises(ValueError, match="path traversal"):
        workspace_path("owner/repo\\..\\..\\etc\\passwd", dest)


def test_empty_model_id_rejected():
    """Empty model_id is rejected."""
    dest = "/tmp/test_downloads"
    with pytest.raises(ValueError, match="must not be empty"):
        workspace_path("", dest)


def test_no_namespace_rejected():
    """Model ID without namespace/repository format is rejected."""
    dest = "/tmp/test_downloads"
    with pytest.raises(ValueError, match="namespace/repository format"):
        workspace_path("model-name", dest)


def test_path_stays_under_destination():
    """Returned path remains under destination."""
    dest = "/some/custom/destination"
    path = workspace_path("owner/repo", dest)
    assert str(path).startswith(dest)
    assert path == Path(dest) / "owner/repo"


def test_invalid_characters_rejected():
    """Model IDs with invalid characters are rejected."""
    dest = "/tmp/test_downloads"

    with pytest.raises(ValueError, match="invalid characters"):
        workspace_path("owner@repo/something", dest)

    with pytest.raises(ValueError, match="invalid characters"):
        workspace_path("owner#repo/something", dest)


def test_valid_characters_allowed():
    """Model IDs with valid characters are accepted."""
    dest = "/tmp/test_downloads"

    path1 = workspace_path("owner/repo_name", dest)
    assert path1 == Path(dest) / "owner/repo_name"

    path2 = workspace_path("owner/repo-name", dest)
    assert path2 == Path(dest) / "owner/repo-name"

    path3 = workspace_path("owner/repo.name", dest)
    assert path3 == Path(dest) / "owner/repo.name"
