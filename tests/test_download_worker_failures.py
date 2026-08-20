from __future__ import annotations

from src.download_worker import worker


def test_worker_marks_failed_and_continues(
    monkeypatch,
):
    queued_model = (
        1,
        "example/missing-model",
        "Example",
        "1.0",
        "QUEUED",
    )

    queue_reads = 0
    calls: list[tuple] = []

    def get_queued_models():
        nonlocal queue_reads

        queue_reads += 1

        if queue_reads == 1:
            return [
                queued_model
            ]

        return []

    monkeypatch.setattr(
        worker,
        "get_queued_models",
        get_queued_models,
    )

    monkeypatch.setattr(
        worker,
        "get_cached_archive",
        lambda model_id: None,
    )

    monkeypatch.setattr(
        worker,
        "update_model_status",
        lambda model_id, status: calls.append(
            (
                "status",
                model_id,
                status.value,
            )
        ),
    )

    def fail_download(
        model_id,
        destination,
    ):
        raise RuntimeError(
            "simulated download failure"
        )

    monkeypatch.setattr(
        worker,
        "download_repository",
        fail_download,
    )

    monkeypatch.setattr(
        worker,
        "mark_failed",
        lambda model_id, error_message: calls.append(
            (
                "failed",
                model_id,
                error_message,
            )
        ),
    )

    def stop_when_queue_empty(
        seconds,
    ):
        raise KeyboardInterrupt()

    monkeypatch.setattr(
        worker.time,
        "sleep",
        stop_when_queue_empty,
    )

    try:
        worker.process_queue()
    except KeyboardInterrupt:
        pass

    assert queue_reads == 2

    assert (
        "status",
        "example/missing-model",
        "DOWNLOADING",
    ) in calls

    failed = [
        item
        for item in calls
        if item[0] == "failed"
    ]

    assert len(failed) == 1

    assert (
        failed[0][1]
        == "example/missing-model"
    )

    assert (
        "simulated download failure"
        in failed[0][2]
    )