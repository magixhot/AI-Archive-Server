import sqlite3
from pathlib import Path


DATABASE_PATH = (
    Path(__file__).resolve().parents[2]
    / "registry"
    / "data"
    / "registry.db"
)


def get_queued_models():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            model_id,
            family,
            version,
            status
        FROM models
        WHERE status = 'QUEUED'
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return rows


def update_model_status(
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