from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.provenance.service import (
    UpstreamProvenance,
    RefreshResult,
    read_provenance,
    write_provenance,
    refresh_metadata,
    _resolve_upstream_info,
)


def _create_model_archive(
    root: Path,
    model_id: str = "Qwen/Qwen3-0.6B",
    family: str = "Qwen",
) -> Path:
    model_path = root / family / model_id.split("/")[1]
    model_path.mkdir(parents=True, exist_ok=True)

    manifest = {
        "archive_version": "1.0",
        "model_id": model_id,
        "family": family,
        "version": "0.6B",
        "status": "ARCHIVED",
        "created": "2026-07-28T06:40:01.033961",
        "storage": {
            "repository": "repository/",
            "metadata": "metadata/",
        },
        "metadata": {
            "model": "metadata/model.json",
            "files": "metadata/files.json",
        },
    }

    with open(
        model_path / "manifest.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(manifest, f, indent=2)

    (model_path / "repository").mkdir(
        exist_ok=True
    )
    (model_path / "metadata").mkdir(
        exist_ok=True
    )

    return model_path


def _create_provenance_file(
    model_path: Path,
    model_id: str = "Qwen/Qwen3-0.6B",
    revision: str = "abc123def456",
) -> None:
    provenance = UpstreamProvenance(
        model_id=model_id,
        upstream_provider="huggingface",
        upstream_revision=revision,
        upstream_url=f"https://huggingface.co/{model_id}",
        declared_revision=None,
        recorded_at="2026-08-22T00:00:00+00:00",
    )
    write_provenance(model_path, provenance)


class TestUpstreamProvenance:
    def test_to_dict(self) -> None:
        p = UpstreamProvenance(
            model_id="test/model",
            upstream_provider="huggingface",
            upstream_revision="abc123",
            upstream_url="https://huggingface.co/test/model",
            declared_revision=None,
            recorded_at="2026-08-22T00:00:00",
        )
        d = p.to_dict()
        assert d["model_id"] == "test/model"
        assert d["upstream_revision"] == "abc123"
        assert d["upstream_provider"] == "huggingface"

    def test_from_dict(self) -> None:
        data = {
            "model_id": "test/model",
            "upstream_provider": "huggingface",
            "upstream_revision": "abc123",
            "upstream_url": "https://huggingface.co/test/model",
            "declared_revision": None,
            "recorded_at": "2026-08-22T00:00:00",
        }
        p = UpstreamProvenance.from_dict(data)
        assert p.model_id == "test/model"
        assert p.upstream_revision == "abc123"

    def test_from_dict_defaults(self) -> None:
        p = UpstreamProvenance.from_dict({})
        assert p.model_id == ""
        assert p.upstream_provider == "huggingface"
        assert p.upstream_revision is None


class TestReadProvenance:
    def test_read_provenance_returns_none_when_missing(
        self, tmp_path: Path
    ) -> None:
        result = read_provenance(tmp_path)
        assert result is None

    def test_read_provenance_returns_provenance_when_exists(
        self, tmp_path: Path
    ) -> None:
        _create_provenance_file(
            tmp_path,
            model_id="test/model",
            revision="abc123",
        )
        result = read_provenance(tmp_path)
        assert result is not None
        assert result.model_id == "test/model"
        assert result.upstream_revision == "abc123"

    def test_read_provenance_returns_none_on_corrupt_file(
        self, tmp_path: Path
    ) -> None:
        metadata_dir = tmp_path / "metadata"
        metadata_dir.mkdir()
        provenance_file = metadata_dir / "provenance.json"
        provenance_file.write_text(
            "not valid json", encoding="utf-8"
        )
        result = read_provenance(tmp_path)
        assert result is None


class TestWriteProvenance:
    def test_write_creates_file(
        self, tmp_path: Path
    ) -> None:
        provenance = UpstreamProvenance(
            model_id="test/model",
            upstream_provider="huggingface",
            upstream_revision="abc123",
        )
        path = write_provenance(tmp_path, provenance)
        assert path.exists()

        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["model_id"] == "test/model"
        assert data["upstream_revision"] == "abc123"

    def test_write_creates_parent_directories(
        self, tmp_path: Path
    ) -> None:
        provenance = UpstreamProvenance(
            model_id="test/model",
            upstream_provider="huggingface",
        )
        path = write_provenance(tmp_path, provenance)
        assert path.parent.exists()

    def test_write_overwrites_existing(
        self, tmp_path: Path
    ) -> None:
        _create_provenance_file(
            tmp_path, revision="old_rev"
        )
        new_provenance = UpstreamProvenance(
            model_id="test/model",
            upstream_provider="huggingface",
            upstream_revision="new_rev",
        )
        write_provenance(tmp_path, new_provenance)
        result = read_provenance(tmp_path)
        assert result is not None
        assert result.upstream_revision == "new_rev"


class TestResolveUpstreamInfo:
    @patch(
        "src.hf_client.client.get_model_info"
    )
    def test_resolve_returns_provenance(
        self, mock_get_model_info: MagicMock
    ) -> None:
        mock_info = MagicMock()
        mock_info.sha = "abc123def456"
        mock_get_model_info.return_value = mock_info

        result = _resolve_upstream_info(
            "Qwen/Qwen3-0.6B"
        )

        assert result is not None
        assert result.model_id == "Qwen/Qwen3-0.6B"
        assert result.upstream_revision == "abc123def456"
        assert result.upstream_provider == "huggingface"
        assert (
            result.upstream_url
            == "https://huggingface.co/Qwen/Qwen3-0.6B"
        )
        assert result.recorded_at is not None

    @patch(
        "src.hf_client.client.get_model_info"
    )
    def test_resolve_returns_none_on_exception(
        self, mock_get_model_info: MagicMock
    ) -> None:
        mock_get_model_info.side_effect = Exception(
            "Network error"
        )
        result = _resolve_upstream_info(
            "Qwen/Qwen3-0.6B"
        )
        assert result is None


class TestRefreshMetadata:
    @patch(
        "src.provenance.service._resolve_upstream_info"
    )
    def test_creates_provenance_when_missing(
        self,
        mock_resolve: MagicMock,
        tmp_path: Path,
    ) -> None:
        model_path = _create_model_archive(tmp_path)

        mock_upstream = UpstreamProvenance(
            model_id="Qwen/Qwen3-0.6B",
            upstream_provider="huggingface",
            upstream_revision="abc123",
            upstream_url="https://huggingface.co/Qwen/Qwen3-0.6B",
            recorded_at="2026-08-22T00:00:00+00:00",
        )
        mock_resolve.return_value = mock_upstream

        result = refresh_metadata(
            "Qwen/Qwen3-0.6B",
            model_path,
        )

        assert result.provenance_changed is True
        assert result.upstream_changed is False
        assert result.upstream_revision == "abc123"
        assert result.previous_revision is None
        assert "created" in result.message

        provenance = read_provenance(model_path)
        assert provenance is not None
        assert provenance.upstream_revision == "abc123"

    @patch(
        "src.provenance.service._resolve_upstream_info"
    )
    def test_detects_unchanged_upstream(
        self,
        mock_resolve: MagicMock,
        tmp_path: Path,
    ) -> None:
        model_path = _create_model_archive(tmp_path)
        _create_provenance_file(
            model_path, revision="abc123"
        )

        mock_upstream = UpstreamProvenance(
            model_id="Qwen/Qwen3-0.6B",
            upstream_provider="huggingface",
            upstream_revision="abc123",
            upstream_url="https://huggingface.co/Qwen/Qwen3-0.6B",
            recorded_at="2026-08-22T00:00:00+00:00",
        )
        mock_resolve.return_value = mock_upstream

        result = refresh_metadata(
            "Qwen/Qwen3-0.6B",
            model_path,
        )

        assert result.provenance_changed is False
        assert result.upstream_changed is False
        assert result.upstream_revision == "abc123"
        assert result.previous_revision == "abc123"
        assert "unchanged" in result.message

    @patch(
        "src.provenance.service._resolve_upstream_info"
    )
    def test_detects_changed_upstream(
        self,
        mock_resolve: MagicMock,
        tmp_path: Path,
    ) -> None:
        model_path = _create_model_archive(tmp_path)
        _create_provenance_file(
            model_path, revision="old_rev"
        )

        mock_upstream = UpstreamProvenance(
            model_id="Qwen/Qwen3-0.6B",
            upstream_provider="huggingface",
            upstream_revision="new_rev",
            upstream_url="https://huggingface.co/Qwen/Qwen3-0.6B",
            recorded_at="2026-08-22T00:00:00+00:00",
        )
        mock_resolve.return_value = mock_upstream

        result = refresh_metadata(
            "Qwen/Qwen3-0.6B",
            model_path,
        )

        assert result.provenance_changed is True
        assert result.upstream_changed is True
        assert result.upstream_revision == "new_rev"
        assert result.previous_revision == "old_rev"
        assert "changed" in result.message

    @patch(
        "src.provenance.service._resolve_upstream_info"
    )
    def test_handles_unavailable_upstream(
        self,
        mock_resolve: MagicMock,
        tmp_path: Path,
    ) -> None:
        model_path = _create_model_archive(tmp_path)
        _create_provenance_file(
            model_path, revision="abc123"
        )

        mock_resolve.return_value = None

        result = refresh_metadata(
            "Qwen/Qwen3-0.6B",
            model_path,
        )

        assert result.provenance_changed is False
        assert result.upstream_changed is False
        assert result.upstream_revision == "abc123"
        assert result.previous_revision == "abc123"
        assert "unavailable" in result.message

    @patch(
        "src.provenance.service._resolve_upstream_info"
    )
    def test_handles_unavailable_no_existing_provenance(
        self,
        mock_resolve: MagicMock,
        tmp_path: Path,
    ) -> None:
        model_path = _create_model_archive(tmp_path)
        mock_resolve.return_value = None

        result = refresh_metadata(
            "Qwen/Qwen3-0.6B",
            model_path,
        )

        assert result.provenance_changed is False
        assert result.upstream_changed is False
        assert result.upstream_revision is None
        assert result.previous_revision is None
        assert "unavailable" in result.message

    @patch(
        "src.provenance.service._resolve_upstream_info"
    )
    def test_preserves_existing_archive_content(
        self,
        mock_resolve: MagicMock,
        tmp_path: Path,
    ) -> None:
        model_path = _create_model_archive(tmp_path)

        original_manifest = (
            model_path / "manifest.json"
        ).read_text(encoding="utf-8")

        mock_upstream = UpstreamProvenance(
            model_id="Qwen/Qwen3-0.6B",
            upstream_provider="huggingface",
            upstream_revision="abc123",
            recorded_at="2026-08-22T00:00:00+00:00",
        )
        mock_resolve.return_value = mock_upstream

        refresh_metadata(
            "Qwen/Qwen3-0.6B",
            model_path,
        )

        assert (
            model_path / "manifest.json"
        ).read_text(encoding="utf-8") == original_manifest


class TestRegistryUpstreamProvenance:
    def test_update_upstream_provenance(
        self, tmp_path: Path
    ) -> None:
        from src.model_registry import service

        db_path = tmp_path / "test.db"
        schema_path = (
            Path(__file__).resolve().parents[1]
            / "registry"
            / "schema.sql"
        )
        migrations_dir = (
            Path(__file__).resolve().parents[1]
            / "registry"
            / "migrations"
        )

        import sqlite3

        conn = sqlite3.connect(db_path)
        conn.executescript(
            schema_path.read_text(encoding="utf-8")
        )
        for m in sorted(
            migrations_dir.glob("*.sql")
        ):
            conn.executescript(
                m.read_text(encoding="utf-8")
            )
        conn.close()

        with patch.object(
            service,
            "DATABASE_PATH",
            db_path,
        ):
            from src.model_registry.models import (
                ModelRecord,
            )

            record = ModelRecord(
                model_id="Qwen/Qwen3-0.6B",
                family="Qwen",
                version="0.6B",
                status="ARCHIVED",
            )
            service.add_model(record)

            result = service.update_upstream_provenance(
                "Qwen/Qwen3-0.6B",
                "abc123def456",
            )
            assert result is True

            model = service.get_model(
                "Qwen/Qwen3-0.6B"
            )
            assert (
                model["upstream_revision"]
                == "abc123def456"
            )
            assert (
                model["upstream_revision_recorded"]
                is not None
            )
            assert (
                model["metadata_refreshed_at"]
                is not None
            )

    def test_update_provenance_nonexistent_model(
        self, tmp_path: Path
    ) -> None:
        from src.model_registry import service

        db_path = tmp_path / "test.db"
        schema_path = (
            Path(__file__).resolve().parents[1]
            / "registry"
            / "schema.sql"
        )
        migrations_dir = (
            Path(__file__).resolve().parents[1]
            / "registry"
            / "migrations"
        )

        import sqlite3

        conn = sqlite3.connect(db_path)
        conn.executescript(
            schema_path.read_text(encoding="utf-8")
        )
        for m in sorted(
            migrations_dir.glob("*.sql")
        ):
            conn.executescript(
                m.read_text(encoding="utf-8")
            )
        conn.close()

        with patch.object(
            service,
            "DATABASE_PATH",
            db_path,
        ):
            result = service.update_upstream_provenance(
                "nonexistent/model",
                "abc123",
            )
            assert result is False
