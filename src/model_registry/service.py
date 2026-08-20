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


# --------------------------------------------------
# Query Layer
# --------------------------------------------------


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
            sha256,
            archive_created,
            archive_validated,
            last_verified
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
            sha256,
            archive_created,
            archive_validated,
            last_verified
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


# --------------------------------------------------
# Metadata
# --------------------------------------------------


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
            sha256 = ?
        WHERE model_id = ?
        """,
        (
            storage_path,
            size_bytes,
            sha256,
            model_id,
        ),
    )

    connection.commit()

    connection.close()


# --------------------------------------------------
# Lifecycle
# --------------------------------------------------


def update_status(
    model_id: str,
    status,
):

    print(
        "DEBUG update_status:",
        model_id,
        status,
        type(status),
    )
    
    
    if isinstance(status, str):

        status = ModelStatus(
            status
        )


    connection = get_connection()

    cursor = connection.cursor()

    now = datetime.utcnow().isoformat()


    if status == ModelStatus.DOWNLOADING:

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
                now,
                model_id,
            ),
        )


    elif status == ModelStatus.DOWNLOADED:

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
                now,
                model_id,
            ),
        )


    else:

        cursor.execute(
            """
            UPDATE models
            SET
                status = ?
            WHERE model_id = ?
            """,
            (
                status.value,
                model_id,
            ),
        )


    connection.commit()

    connection.close()


def mark_archive_created(
    model_id: str,
):

    connection = get_connection()

    cursor = connection.cursor()

    now = datetime.utcnow().isoformat()


    cursor.execute(
        """
        UPDATE models
        SET
            status = ?,
            archive_created = ?
        WHERE model_id = ?
        """,
        (
            ModelStatus.ARCHIVED.value,
            now,
            model_id,
        ),
    )


    connection.commit()

    connection.close()



def mark_archive_validated(
    model_id: str,
):

    connection = get_connection()

    cursor = connection.cursor()

    now = datetime.utcnow().isoformat()


    cursor.execute(
        """
        UPDATE models
        SET
            status = ?,
            archive_validated = ?,
            last_verified = ?
        WHERE model_id = ?
        """,
        (
            ModelStatus.VALIDATED.value,
            now,
            now,
            model_id,
        ),
    )


    connection.commit()

    connection.close()



def mark_ready(
    model_id: str,
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE models
        SET
            status = ?
        WHERE model_id = ?
        """,
        (
            ModelStatus.READY.value,
            model_id,
        ),
    )


    connection.commit()

    connection.close()



def mark_failed(
    model_id: str,
    error_message: str | None = None,
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE models
        SET
            status = ?,
            error_message = ?
        WHERE model_id = ?
        """,
        (
            ModelStatus.FAILED.value,
            error_message,
            model_id,
        ),
    )


    connection.commit()

    connection.close()

def retry_failed(
    model_id: str,
) -> bool:

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT status
        FROM models
        WHERE model_id = ?
        """,
        (
            model_id,
        ),
    )

    row = cursor.fetchone()

    if row is None:
        connection.close()
        return False

    if row[0] != ModelStatus.FAILED.value:
        connection.close()
        return False

    cursor.execute(
        """
        UPDATE models
        SET
            status = ?,
            error_message = NULL
        WHERE model_id = ?
        """,
        (
            ModelStatus.QUEUED.value,
            model_id,
        ),
    )

    connection.commit()

    connection.close()

    return True
