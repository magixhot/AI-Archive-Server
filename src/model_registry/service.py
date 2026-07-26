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



def get_connection():

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return sqlite3.connect(
        DATABASE_PATH
    )



def model_exists(
    model_id: str,
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM models
        WHERE model_id = ?
        """,
        (
            model_id,
        ),
    )

    result = cursor.fetchone()

    connection.close()

    return result is not None



def add_model(
    model: ModelRecord,
):

    if model_exists(
        model.model_id
    ):
        return


    connection = get_connection()

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

    connection = get_connection()

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



# HF-0006 Query Layer


def get_all_models():

    connection = get_connection()

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            model_id,
            family,
            version,
            status,
            storage_path,
            size_bytes,
            sha256
        FROM models
        ORDER BY model_id
        """
    )

    rows = cursor.fetchall()

    connection.close()


    return [
        dict(row)
        for row in rows
    ]



def get_model(
    model_id: str,
):

    connection = get_connection()

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            model_id,
            family,
            version,
            status,
            storage_path,
            size_bytes,
            sha256
        FROM models
        WHERE model_id = ?
        """,
        (
            model_id,
        ),
    )

    row = cursor.fetchone()

    connection.close()


    if row is None:

        return None


    return dict(row)



def get_families():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT DISTINCT family
        FROM models
        WHERE family IS NOT NULL
        ORDER BY family
        """
    )

    rows = cursor.fetchall()

    connection.close()


    return [
        row[0]
        for row in rows
    ]



def update_model_metadata(
    model_id: str,
    storage_path: str | None = None,
    size_bytes: int | None = None,
    sha256: str | None = None,
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE models
        SET
            storage_path = ?,
            size_bytes = ?,
            sha256 = ?,
            verified_at = ?
        WHERE model_id = ?
        """,
        (
            storage_path,
            size_bytes,
            sha256,
            datetime.utcnow().isoformat(),
            model_id,
        ),
    )

    connection.commit()

    connection.close()



def update_status(
    model_id: str,
    status,
):

    if isinstance(status, str):

        status = ModelStatus(
            status
        )


    connection = get_connection()

    cursor = connection.cursor()


    if status == ModelStatus.DOWNLOADING:

        download_started = (
            datetime.utcnow()
            .isoformat()
        )

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

        download_finished = (
            datetime.utcnow()
            .isoformat()
        )

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