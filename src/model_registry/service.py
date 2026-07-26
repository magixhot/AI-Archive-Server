from datetime import datetime

import sqlite3

from pathlib import Path

from .models import ModelRecord

from .states import ModelStatus

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_PATH = (
    BASE_DIR
    / "registry"
    / "data"
    / "registry.db"
)


def model_exists(model_id: str):

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM models
        WHERE model_id = ?
        """,
        (model_id,),
    )

    result = cursor.fetchone()

    connection.close()

    return result is not None



def add_model(model: ModelRecord):

    if model_exists(model.model_id):
        return

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



from datetime import datetime

# ... остальные импорты остаются без изменений ...


def update_status(
    model_id: str,
    status,
):

    if isinstance(status, str):
        status = ModelStatus(status)

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    download_started = None
    download_finished = None

    if status == ModelStatus.DOWNLOADING:
        download_started = datetime.utcnow().isoformat()

        cursor.execute(
            """
            UPDATE models
            SET
                status = ?,
                download_started = ?
            WHERE model_id = ?
            """,
            (
                status.value,
                download_started,
                model_id,
            ),
        )

    elif status == ModelStatus.DOWNLOADED:
        download_finished = datetime.utcnow().isoformat()

        cursor.execute(
            """
            UPDATE models
            SET
                status = ?,
                download_finished = ?
            WHERE model_id = ?
            """,
            (
                status.value,
                download_finished,
                model_id,
            ),
        )

    else:

        cursor.execute(
            """
            UPDATE models
            SET status = ?
            WHERE model_id = ?
            """,
            (
                status.value,
                model_id,
            ),
        )

    connection.commit()

    connection.close()