import sqlite3

from pathlib import Path

from .models import ModelRecord


BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_PATH = (
    BASE_DIR
    / "registry"
    / "data"
    / "registry.db"
)


def add_model(model: ModelRecord):

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO models
        (
            model_id,
            family,
            version,
            status,
            storage_path,
            size_bytes,
            sha256
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            model.model_id,
            model.family,
            model.version,
            model.status,
            model.storage_path,
            model.size_bytes,
            model.sha256,
        ),
    )

    connection.commit()

    connection.close()



def get_models():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            model_id,
            family,
            version,
            status
        FROM models
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return rows



def update_status(
    model_id: str,
    status: str,
):

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE models
        SET status = ?
        WHERE model_id = ?
        """,
        (
            status,
            model_id,
        ),
    )

    connection.commit()

    connection.close()