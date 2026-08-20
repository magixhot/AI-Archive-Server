from __future__ import annotations

from src.model_registry import api


def test_retry_failed_model_queues_it(
    monkeypatch,
):
    monkeypatch.setattr(
        api,
        "get_model",
        lambda model_id: {
            "model_id": model_id,
            "status": "FAILED",
        },
    )

    monkeypatch.setattr(
        api,
        "retry_failed",
        lambda model_id: True,
    )

    result = api.retry_model(
        "example/model"
    )

    assert result == {
        "model_id": "example/model",
        "status": "QUEUED",
        "retried": True,
    }


def test_retry_non_failed_model_is_rejected(
    monkeypatch,
):
    monkeypatch.setattr(
        api,
        "get_model",
        lambda model_id: {
            "model_id": model_id,
            "status": "VALIDATED",
        },
    )

    monkeypatch.setattr(
        api,
        "retry_failed",
        lambda model_id: False,
    )

    result = api.retry_model(
        "Qwen/Qwen3-0.6B"
    )

    assert result == {
        "model_id": "Qwen/Qwen3-0.6B",
        "status": "VALIDATED",
        "retried": False,
        "error": "Model is not FAILED",
    }


def test_retry_unknown_model_is_rejected(
    monkeypatch,
):
    monkeypatch.setattr(
        api,
        "get_model",
        lambda model_id: None,
    )

    result = api.retry_model(
        "unknown/model"
    )

    assert result == {
        "model_id": "unknown/model",
        "retried": False,
        "error": "Model not found",
    }

def test_retry_failed_clears_download_lifecycle(
    monkeypatch,
    tmp_path,
):
    import sqlite3

    from src.model_registry import service

    db_path = tmp_path / "registry.db"

    connection = sqlite3.connect(db_path)

    connection.execute(
        """
        CREATE TABLE models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id TEXT UNIQUE NOT NULL,
            status TEXT,
            error_message TEXT,
            download_started TEXT,
            download_finished TEXT
        )
        """
    )

    connection.execute(
        """
        INSERT INTO models (
            model_id,
            status,
            error_message,
            download_started,
            download_finished
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "example/retry-test",
            "FAILED",
            "simulated failure",
            "2026-08-20T10:00:00",
            "2026-08-20T10:05:00",
        ),
    )

    connection.commit()
    connection.close()

    monkeypatch.setattr(
        service,
        "DATABASE_PATH",
        db_path,
    )

    result = service.retry_failed(
        "example/retry-test"
    )

    assert result is True

    connection = sqlite3.connect(db_path)

    row = connection.execute(
        """
        SELECT
            status,
            error_message,
            download_started,
            download_finished
        FROM models
        WHERE model_id = ?
        """,
        (
            "example/retry-test",
        ),
    ).fetchone()

    connection.close()

    assert row == (
        "QUEUED",
        None,
        None,
        None,
    )