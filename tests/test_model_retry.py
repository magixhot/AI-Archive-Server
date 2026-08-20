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