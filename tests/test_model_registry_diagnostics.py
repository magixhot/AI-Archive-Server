from __future__ import annotations

import sqlite3

from src.model_registry import service


def test_get_model_includes_error_message(
    monkeypatch,
    tmp_path,
):
    db_path = tmp_path / "registry.db"

    connection = sqlite3.connect(db_path)

    connection.execute(
        """
        CREATE TABLE models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id TEXT UNIQUE NOT NULL,
            family TEXT,
            version TEXT,
            status TEXT,
            storage_path TEXT,
            size_bytes INTEGER,
            sha256 TEXT,
            error_message TEXT,
            archive_created TEXT,
            archive_validated TEXT,
            last_verified TEXT,
            upstream_revision TEXT,
            upstream_revision_recorded TIMESTAMP,
            metadata_refreshed_at TIMESTAMP
        )
        """
    )

    connection.execute(
        """
        INSERT INTO models (
            model_id,
            family,
            version,
            status,
            error_message
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "example/failed-model",
            "Example",
            "1.0",
            "FAILED",
            "simulated failure",
        ),
    )

    connection.commit()
    connection.close()

    monkeypatch.setattr(
        service,
        "DATABASE_PATH",
        db_path,
    )

    result = service.get_model(
        "example/failed-model"
    )

    assert result is not None
    assert result["status"] == "FAILED"
    assert result["error_message"] == "simulated failure"


def test_get_all_models_includes_error_message(
    monkeypatch,
    tmp_path,
):
    db_path = tmp_path / "registry.db"

    connection = sqlite3.connect(db_path)

    connection.execute(
        """
        CREATE TABLE models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id TEXT UNIQUE NOT NULL,
            family TEXT,
            version TEXT,
            status TEXT,
            storage_path TEXT,
            size_bytes INTEGER,
            sha256 TEXT,
            error_message TEXT,
            archive_created TEXT,
            archive_validated TEXT,
            last_verified TEXT,
            upstream_revision TEXT,
            upstream_revision_recorded TIMESTAMP,
            metadata_refreshed_at TIMESTAMP
        )
        """
    )

    connection.execute(
        """
        INSERT INTO models (
            model_id,
            family,
            version,
            status,
            error_message
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "example/failed-model",
            "Example",
            "1.0",
            "FAILED",
            "simulated failure",
        ),
    )

    connection.commit()
    connection.close()

    monkeypatch.setattr(
        service,
        "DATABASE_PATH",
        db_path,
    )

    result = service.get_all_models()

    assert len(result) == 1
    assert result[0]["status"] == "FAILED"
    assert result[0]["error_message"] == "simulated failure"
