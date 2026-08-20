from __future__ import annotations

from src.model_registry import api


def test_register_model_returns_existing_status(
    monkeypatch,
):
    monkeypatch.setattr(
        api,
        "model_exists",
        lambda model_id: True,
    )

    monkeypatch.setattr(
        api,
        "get_model",
        lambda model_id: {
            "model_id": model_id,
            "status": "VALIDATED",
        },
    )

    add_calls: list[object] = []

    monkeypatch.setattr(
        api,
        "add_model",
        lambda model: add_calls.append(model),
    )

    result = api.register_model(
        "Qwen/Qwen3-0.6B",
        family="Qwen",
        version="0.6B",
    )

    assert result == {
        "model_id": "Qwen/Qwen3-0.6B",
        "status": "VALIDATED",
        "existing": True,
    }

    assert add_calls == []


def test_register_model_queues_new_model(
    monkeypatch,
):
    monkeypatch.setattr(
        api,
        "model_exists",
        lambda model_id: False,
    )

    added_models: list[object] = []

    monkeypatch.setattr(
        api,
        "add_model",
        lambda model: added_models.append(model),
    )

    result = api.register_model(
        "example/test-model",
        family="Example",
        version="1.0",
    )

    assert result == {
        "model_id": "example/test-model",
        "status": "QUEUED",
        "existing": False,
    }

    assert len(added_models) == 1

    model = added_models[0]

    assert model.model_id == "example/test-model"
    assert model.family == "Example"
    assert model.version == "1.0"
    assert model.status == "QUEUED"