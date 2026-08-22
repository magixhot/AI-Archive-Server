from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parents[2]

REGISTRY_DIR = BASE_DIR / "registry"

DATABASE_PATH = REGISTRY_DIR / "data" / "registry.db"

SCHEMA_PATH = REGISTRY_DIR / "schema.sql"

MIGRATIONS_DIR = REGISTRY_DIR / "migrations"


KNOWN_MIGRATION_COLUMNS = {
    "001_add_download_metadata.sql": {
        "download_started",
        "download_finished",
        "error_message",
    },
    "002_add_archive_lifecycle.sql": {
        "archive_created",
        "archive_validated",
        "last_verified",
    },
    "003_add_upstream_provenance.sql": {
        "upstream_revision",
        "upstream_revision_recorded",
        "metadata_refreshed_at",
    },
}


@dataclass
class BootstrapResult:
    applied: list[str] = field(
        default_factory=list
    )

    skipped: list[str] = field(
        default_factory=list
    )

    reconciled: list[str] = field(
        default_factory=list
    )

    @property
    def changed(self) -> bool:
        return bool(
            self.applied
            or self.reconciled
        )

    def to_dict(self) -> dict:
        return {
            "changed": self.changed,
            "applied": self.applied,
            "skipped": self.skipped,
            "reconciled": self.reconciled,
        }


def _get_connection(
    database_path: Path,
) -> sqlite3.Connection:
    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return sqlite3.connect(
        database_path
    )


def _read_sql(
    path: Path,
) -> str:
    return path.read_text(
        encoding="utf-8"
    )


def _get_model_columns(
    connection: sqlite3.Connection,
) -> set[str]:
    rows = connection.execute(
        "PRAGMA table_info(models)"
    ).fetchall()

    return {
        row[1]
        for row in rows
    }


def _migration_recorded(
    connection: sqlite3.Connection,
    filename: str,
) -> bool:
    row = connection.execute(
        """
        SELECT 1
        FROM migrations
        WHERE filename = ?
        """,
        (filename,),
    ).fetchone()

    return row is not None


def _record_migration(
    connection: sqlite3.Connection,
    filename: str,
) -> None:
    connection.execute(
        """
        INSERT OR IGNORE INTO migrations (
            filename
        )
        VALUES (?)
        """,
        (filename,),
    )


def bootstrap_registry(
    *,
    registry_dir: str | Path = REGISTRY_DIR,
) -> BootstrapResult:
    registry_dir = Path(
        registry_dir
    ).resolve()

    database_path = (
        registry_dir
        / "data"
        / "registry.db"
    )

    schema_path = (
        registry_dir
        / "schema.sql"
    )

    migrations_dir = (
        registry_dir
        / "migrations"
    )

    if not schema_path.is_file():
        raise FileNotFoundError(
            f"Registry schema not found: "
            f"{schema_path}"
        )

    if not migrations_dir.is_dir():
        raise FileNotFoundError(
            f"Registry migrations not found: "
            f"{migrations_dir}"
        )

    result = BootstrapResult()

    connection = _get_connection(
        database_path
    )

    try:
        connection.executescript(
            _read_sql(
                schema_path
            )
        )

        migration_files = sorted(
            migrations_dir.glob(
                "*.sql"
            )
        )

        for migration_path in migration_files:
            filename = migration_path.name

            if filename == (
                "000_create_migration_table.sql"
            ):
                connection.executescript(
                    _read_sql(
                        migration_path
                    )
                )

                if not _migration_recorded(
                    connection,
                    filename,
                ):
                    _record_migration(
                        connection,
                        filename,
                    )
                    result.applied.append(
                        filename
                    )
                else:
                    result.skipped.append(
                        filename
                    )

                connection.commit()
                continue

            if _migration_recorded(
                connection,
                filename,
            ):
                result.skipped.append(
                    filename
                )
                continue

            expected_columns = (
                KNOWN_MIGRATION_COLUMNS.get(
                    filename
                )
            )

            if expected_columns:
                existing_columns = (
                    _get_model_columns(
                        connection
                    )
                )

                if expected_columns.issubset(
                    existing_columns
                ):
                    _record_migration(
                        connection,
                        filename,
                    )

                    connection.commit()

                    result.reconciled.append(
                        filename
                    )

                    continue

            connection.executescript(
                _read_sql(
                    migration_path
                )
            )

            _record_migration(
                connection,
                filename,
            )

            connection.commit()

            result.applied.append(
                filename
            )

    finally:
        connection.close()

    return result


def main() -> None:
    result = bootstrap_registry()

    print(
        "Registry bootstrap:",
        result.to_dict(),
    )


if __name__ == "__main__":
    main()