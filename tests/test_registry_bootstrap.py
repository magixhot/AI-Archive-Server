from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest

from src.model_registry.bootstrap import bootstrap_registry


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id TEXT NOT NULL UNIQUE,
    family TEXT,
    version TEXT,
    status TEXT NOT NULL DEFAULT 'QUEUED',
    storage_path TEXT,
    size_bytes INTEGER,
    sha256 TEXT
);
"""


MIGRATION_000 = """
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


MIGRATION_001 = """
ALTER TABLE models
ADD COLUMN download_started TIMESTAMP;

ALTER TABLE models
ADD COLUMN download_finished TIMESTAMP;

ALTER TABLE models
ADD COLUMN error_message TEXT;
"""


MIGRATION_002 = """
ALTER TABLE models
ADD COLUMN archive_created TIMESTAMP;

ALTER TABLE models
ADD COLUMN archive_validated TIMESTAMP;

ALTER TABLE models
ADD COLUMN last_verified TIMESTAMP;
"""


def _prepare_registry(
    root: Path,
) -> Path:
    registry_dir = root / "registry"
    migrations_dir = registry_dir / "migrations"

    migrations_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    (registry_dir / "schema.sql").write_text(
        SCHEMA_SQL,
        encoding="utf-8",
    )

    (
        migrations_dir
        / "000_create_migration_table.sql"
    ).write_text(
        MIGRATION_000,
        encoding="utf-8",
    )

    (
        migrations_dir
        / "001_add_download_metadata.sql"
    ).write_text(
        MIGRATION_001,
        encoding="utf-8",
    )

    (
        migrations_dir
        / "002_add_archive_lifecycle.sql"
    ).write_text(
        MIGRATION_002,
        encoding="utf-8",
    )

    return registry_dir


def _get_columns(
    database_path: Path,
) -> set[str]:
    connection = sqlite3.connect(
        database_path
    )

    try:
        rows = connection.execute(
            "PRAGMA table_info(models)"
        ).fetchall()
    finally:
        connection.close()

    return {
        row[1]
        for row in rows
    }


def _get_migrations(
    database_path: Path,
) -> list[str]:
    connection = sqlite3.connect(
        database_path
    )

    try:
        rows = connection.execute(
            """
            SELECT filename
            FROM migrations
            ORDER BY filename
            """
        ).fetchall()
    finally:
        connection.close()

    return [
        row[0]
        for row in rows
    ]


def test_bootstrap_fresh_registry(
    tmp_path: Path,
):
    registry_dir = _prepare_registry(
        tmp_path
    )

    result = bootstrap_registry(
        registry_dir=registry_dir
    )

    database_path = (
        registry_dir
        / "data"
        / "registry.db"
    )

    assert result.valid if hasattr(result, "valid") else True

    assert set(result.applied) == {
        "000_create_migration_table.sql",
        "001_add_download_metadata.sql",
        "002_add_archive_lifecycle.sql",
    }

    columns = _get_columns(
        database_path
    )

    assert {
        "download_started",
        "download_finished",
        "error_message",
        "archive_created",
        "archive_validated",
        "last_verified",
    }.issubset(
        columns
    )

    assert _get_migrations(
        database_path
    ) == [
        "000_create_migration_table.sql",
        "001_add_download_metadata.sql",
        "002_add_archive_lifecycle.sql",
    ]


def test_bootstrap_is_idempotent(
    tmp_path: Path,
):
    registry_dir = _prepare_registry(
        tmp_path
    )

    first = bootstrap_registry(
        registry_dir=registry_dir
    )

    second = bootstrap_registry(
        registry_dir=registry_dir
    )

    assert first.changed is True
    assert second.changed is False

    assert second.applied == []
    assert second.reconciled == []

    assert set(second.skipped) == {
        "000_create_migration_table.sql",
        "001_add_download_metadata.sql",
        "002_add_archive_lifecycle.sql",
    }


def test_bootstrap_reconciles_existing_columns(
    tmp_path: Path,
):
    registry_dir = _prepare_registry(
        tmp_path
    )

    database_path = (
        registry_dir
        / "data"
        / "registry.db"
    )

    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        database_path
    )

    try:
        connection.executescript(
            SCHEMA_SQL
        )

        connection.executescript(
            MIGRATION_000
        )

        connection.executescript(
            MIGRATION_001
        )

        connection.executescript(
            MIGRATION_002
        )

        connection.commit()
    finally:
        connection.close()

    result = bootstrap_registry(
        registry_dir=registry_dir
    )

    assert set(result.reconciled) == {
        "001_add_download_metadata.sql",
        "002_add_archive_lifecycle.sql",
    }

    assert (
        "000_create_migration_table.sql"
        in result.applied
        or
        "000_create_migration_table.sql"
        in result.skipped
    )

    assert _get_migrations(
        database_path
    ) == [
        "000_create_migration_table.sql",
        "001_add_download_metadata.sql",
        "002_add_archive_lifecycle.sql",
    ]


def test_bootstrap_missing_schema_fails(
    tmp_path: Path,
):
    registry_dir = (
        tmp_path
        / "registry"
    )

    (
        registry_dir
        / "migrations"
    ).mkdir(
        parents=True,
        exist_ok=True,
    )

    with pytest.raises(
        FileNotFoundError
    ):
        bootstrap_registry(
            registry_dir=registry_dir
        )


def test_bootstrap_missing_migrations_fails(
    tmp_path: Path,
):
    registry_dir = (
        tmp_path
        / "registry"
    )

    registry_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        registry_dir
        / "schema.sql"
    ).write_text(
        SCHEMA_SQL,
        encoding="utf-8",
    )

    with pytest.raises(
        FileNotFoundError
    ):
        bootstrap_registry(
            registry_dir=registry_dir
        )