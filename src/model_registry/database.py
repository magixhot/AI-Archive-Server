import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

REGISTRY_DIR = BASE_DIR / "registry"

DATABASE_PATH = REGISTRY_DIR / "data" / "registry.db"

SCHEMA_PATH = REGISTRY_DIR / "schema.sql"


def get_connection():
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    return connection


def initialize_database():

    connection = get_connection()

    with open(
        SCHEMA_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        schema = file.read()


    connection.executescript(schema)

    connection.commit()

    connection.close()


if __name__ == "__main__":

    initialize_database()

    print(
        f"Database initialized: {DATABASE_PATH}"
    )