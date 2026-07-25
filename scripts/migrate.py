import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

DATABASE_PATH = (
    BASE_DIR
    / "registry"
    / "data"
    / "registry.db"
)

MIGRATIONS_PATH = (
    BASE_DIR
    / "registry"
    / "migrations"
)


def get_connection():

    return sqlite3.connect(
        DATABASE_PATH
    )


def ensure_migration_table(connection):

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS migrations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            filename TEXT NOT NULL UNIQUE,

            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        );
        """
    )

    connection.commit()


def get_applied_migrations(connection):

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT filename
        FROM migrations
        """
    )

    return {
        row[0]
        for row in cursor.fetchall()
    }


def apply_migration(
    connection,
    filename,
):

    path = MIGRATIONS_PATH / filename

    sql = path.read_text(
        encoding="utf-8"
    )

    cursor = connection.cursor()

    cursor.executescript(sql)

    cursor.execute(
        """
        INSERT INTO migrations(filename)
        VALUES (?)
        """,
        (
            filename,
        ),
    )

    connection.commit()


def migrate():

    connection = get_connection()

    ensure_migration_table(
        connection
    )

    applied = get_applied_migrations(
        connection
    )

    migrations = sorted(
        MIGRATIONS_PATH.glob("*.sql")
    )

    for migration in migrations:

        filename = migration.name

        if filename in applied:
            continue

        print(
            f"Applying {filename}"
        )

        apply_migration(
            connection,
            filename,
        )

    connection.close()


if __name__ == "__main__":

    migrate()