from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from src.scheduler.config import (
    DEFAULT_ARCHIVE_SYNC_INTERVAL,
    DEFAULT_INTEGRITY_INTERVAL,
    DEFAULT_RECONCILIATION_INTERVAL,
    SchedulerConfig,
    TaskConfig,
    ArchiveSyncConfig,
    load_config,
)
from src.scheduler.tasks import TaskResult, run_integrity_check
from src.scheduler.scheduler import (
    SchedulerState,
    TaskState,
    _build_task_states,
    _is_due,
    _run_task,
)


# ----------------------------------------------------------------
# Config tests
# ----------------------------------------------------------------


def test_load_config_defaults_when_file_missing(tmp_path: Path):
    config = load_config(tmp_path / "nonexistent.json")

    assert config.integrity_check.enabled is True
    assert (
        config.integrity_check.interval_seconds
        == DEFAULT_INTEGRITY_INTERVAL
    )
    assert config.reconciliation.enabled is True
    assert (
        config.reconciliation.interval_seconds
        == DEFAULT_RECONCILIATION_INTERVAL
    )
    assert config.archive_sync.enabled is True
    assert (
        config.archive_sync.interval_seconds
        == DEFAULT_ARCHIVE_SYNC_INTERVAL
    )
    assert config.archive_sync.dry_run is True


def test_load_config_from_json(tmp_path: Path):
    config_file = tmp_path / "scheduler.json"
    config_file.write_text(
        json.dumps({
            "tasks": {
                "integrity_check": {
                    "enabled": False,
                    "interval_seconds": 3600,
                },
                "reconciliation": {
                    "enabled": True,
                    "interval_seconds": 7200,
                },
                "archive_sync": {
                    "enabled": True,
                    "interval_seconds": 1800,
                    "dry_run": False,
                },
            }
        }),
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert config.integrity_check.enabled is False
    assert config.integrity_check.interval_seconds == 3600
    assert config.reconciliation.enabled is True
    assert config.reconciliation.interval_seconds == 7200
    assert config.archive_sync.enabled is True
    assert config.archive_sync.interval_seconds == 1800
    assert config.archive_sync.dry_run is False


def test_load_config_invalid_json(tmp_path: Path):
    config_file = tmp_path / "bad.json"
    config_file.write_text("not json {{{", encoding="utf-8")

    config = load_config(config_file)

    assert config.integrity_check.enabled is True
    assert (
        config.integrity_check.interval_seconds
        == DEFAULT_INTEGRITY_INTERVAL
    )


def test_load_config_partial_tasks(tmp_path: Path):
    config_file = tmp_path / "partial.json"
    config_file.write_text(
        json.dumps({
            "tasks": {
                "integrity_check": {
                    "interval_seconds": 600,
                },
            }
        }),
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert config.integrity_check.interval_seconds == 600
    assert (
        config.reconciliation.interval_seconds
        == DEFAULT_RECONCILIATION_INTERVAL
    )


# ----------------------------------------------------------------
# TaskState / scheduling logic tests
# ----------------------------------------------------------------


def test_is_due_when_disabled():
    task = TaskState(
        name="test",
        interval_seconds=100,
        enabled=False,
        last_run=0,
    )

    assert _is_due(task, 200) is False


def test_is_due_when_not_enough_time_passed():
    task = TaskState(
        name="test",
        interval_seconds=100,
        enabled=True,
        last_run=50,
    )

    assert _is_due(task, 120) is False


def test_is_due_when_interval_elapsed():
    task = TaskState(
        name="test",
        interval_seconds=100,
        enabled=True,
        last_run=50,
    )

    assert _is_due(task, 150) is True


def test_is_due_on_first_run():
    task = TaskState(
        name="test",
        interval_seconds=100,
        enabled=True,
        last_run=0,
    )

    assert _is_due(task, 100) is True


def test_build_task_states_from_config():
    config = SchedulerConfig(
        integrity_check=TaskConfig(
            enabled=False,
            interval_seconds=500,
        ),
        reconciliation=TaskConfig(
            enabled=True,
            interval_seconds=1000,
        ),
        archive_sync=ArchiveSyncConfig(
            enabled=True,
            interval_seconds=2000,
            dry_run=True,
        ),
    )

    states = _build_task_states(config)

    assert "integrity_check" in states
    assert "reconciliation" in states
    assert "archive_sync" in states
    assert states["integrity_check"].enabled is False
    assert states["integrity_check"].interval_seconds == 500
    assert states["reconciliation"].interval_seconds == 1000
    assert states["archive_sync"].interval_seconds == 2000


# ----------------------------------------------------------------
# TaskResult tests
# ----------------------------------------------------------------


def test_task_result_to_dict():
    result = TaskResult(
        task_name="test_task",
        success=True,
        message="all good",
        details={"count": 5},
    )

    d = result.to_dict()

    assert d["task_name"] == "test_task"
    assert d["success"] is True
    assert d["message"] == "all good"
    assert d["details"] == {"count": 5}


# ----------------------------------------------------------------
# Integrity check task tests
# ----------------------------------------------------------------


def _create_valid_model(root: Path) -> Path:
    model = root / "Qwen" / "Qwen3-Test"
    repository = model / "repository"
    metadata = model / "metadata"

    repository.mkdir(parents=True)
    metadata.mkdir()

    (model / "manifest.json").write_text(
        '{"model_id": "Qwen/Qwen3-Test"}',
        encoding="utf-8",
    )

    files = [
        {
            "path": "config.json",
            "size": 2,
            "sha256": "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
        }
    ]

    (metadata / "files.json").write_text(
        json.dumps(files),
        encoding="utf-8",
    )

    (repository / "config.json").write_text("{}", encoding="utf-8")

    return model


def test_integrity_check_valid_model(tmp_path: Path):
    _create_valid_model(tmp_path)

    result = run_integrity_check(tmp_path)

    assert result.success is True
    assert result.task_name == "integrity_check"
    assert result.details["total"] == 1
    assert result.details["passed"] == 1
    assert result.details["failed"] == 0


def test_integrity_check_missing_root():
    result = run_integrity_check("/nonexistent/path")

    assert result.success is False
    assert "does not exist" in result.message


def test_integrity_check_empty_root(tmp_path: Path):
    result = run_integrity_check(tmp_path)

    assert result.success is True
    assert result.details["total"] == 0


def test_integrity_check_invalid_model(tmp_path: Path):
    model = tmp_path / "Bad" / "BadModel"
    model.mkdir(parents=True)

    result = run_integrity_check(tmp_path)

    assert result.success is True
    assert result.details["total"] == 1
    assert result.details["failed"] == 1


# ----------------------------------------------------------------
# Reconciliation task tests
# ----------------------------------------------------------------


def test_reconciliation_missing_archive():
    from src.scheduler.tasks import run_reconciliation

    result = run_reconciliation("/nonexistent/path")

    assert result.success is False
    assert "does not exist" in result.message


def test_reconciliation_empty_archive(tmp_path: Path):
    from src.scheduler.tasks import run_reconciliation

    result = run_reconciliation(tmp_path)

    assert result.success is True
    assert result.details["reconciled"] == []


# ----------------------------------------------------------------
# Archive sync task tests
# ----------------------------------------------------------------


def test_archive_sync_missing_source():
    from src.scheduler.tasks import run_archive_sync

    result = run_archive_sync(
        "/nonexistent/source",
        "/nonexistent/target",
    )

    assert result.success is False
    assert "does not exist" in result.message


def test_archive_sync_dry_run(tmp_path: Path):
    from src.scheduler.tasks import run_archive_sync

    source = tmp_path / "source"
    target = tmp_path / "target"

    source.mkdir()
    (source / "file.txt").write_text("data", encoding="utf-8")

    result = run_archive_sync(source, target, dry_run=True)

    assert result.success is True
    assert "dry-run" in result.message
    assert not target.exists()


# ----------------------------------------------------------------
# Scheduler loop tests
# ----------------------------------------------------------------


def test_scheduler_runs_tasks_on_schedule(tmp_path: Path):
    from src.scheduler.scheduler import run_scheduler

    config_file = tmp_path / "scheduler.json"
    config_file.write_text(
        json.dumps({
            "tasks": {
                "integrity_check": {
                    "enabled": True,
                    "interval_seconds": 10,
                },
                "reconciliation": {
                    "enabled": False,
                    "interval_seconds": 10,
                },
                "archive_sync": {
                    "enabled": False,
                    "interval_seconds": 10,
                },
            }
        }),
        encoding="utf-8",
    )

    models_root = tmp_path / "models"
    models_root.mkdir()

    call_count = [0]
    max_calls = 3

    def fake_sleep(seconds: float):
        call_count[0] += 1
        if call_count[0] >= max_calls:
            raise SystemExit("Test limit reached")

    with pytest.raises(SystemExit):
        run_scheduler(
            config_file,
            models_root=models_root,
            archive_root=models_root,
            _sleep_fn=fake_sleep,
        )


def test_scheduler_respects_enabled_flag(tmp_path: Path):
    from src.scheduler.scheduler import run_scheduler

    config_file = tmp_path / "scheduler.json"
    config_file.write_text(
        json.dumps({
            "tasks": {
                "integrity_check": {
                    "enabled": False,
                    "interval_seconds": 1,
                },
                "reconciliation": {
                    "enabled": False,
                    "interval_seconds": 1,
                },
                "archive_sync": {
                    "enabled": False,
                    "interval_seconds": 1,
                },
            }
        }),
        encoding="utf-8",
    )

    models_root = tmp_path / "models"
    models_root.mkdir()

    call_count = [0]

    def fake_sleep(seconds: float):
        call_count[0] += 1
        if call_count[0] >= 2:
            raise SystemExit("Test limit reached")

    with pytest.raises(SystemExit):
        run_scheduler(
            config_file,
            models_root=models_root,
            archive_root=models_root,
            _sleep_fn=fake_sleep,
        )


# ----------------------------------------------------------------
# Task execution dispatch tests
# ----------------------------------------------------------------


def test_run_task_integrity_check(tmp_path: Path):
    models_root = tmp_path / "models"
    models_root.mkdir()

    result = _run_task(
        "integrity_check",
        models_root=models_root,
        archive_root=models_root,
        sync_source=models_root,
        sync_target=tmp_path / "target",
        dry_run=True,
    )

    assert result.task_name == "integrity_check"
    assert result.success is True


def test_run_task_reconciliation(tmp_path: Path):
    archive_root = tmp_path / "archive"
    archive_root.mkdir()

    result = _run_task(
        "reconciliation",
        models_root=archive_root,
        archive_root=archive_root,
        sync_source=archive_root,
        sync_target=tmp_path / "target",
        dry_run=True,
    )

    assert result.task_name == "reconciliation"
    assert result.success is True


def test_run_task_archive_sync(tmp_path: Path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()

    result = _run_task(
        "archive_sync",
        models_root=source,
        archive_root=source,
        sync_source=source,
        sync_target=target,
        dry_run=True,
    )

    assert result.task_name == "archive_sync"
    assert result.success is True


def test_run_task_unknown():
    result = _run_task(
        "nonexistent_task",
        models_root=Path("."),
        archive_root=Path("."),
        sync_source=Path("."),
        sync_target=Path("."),
        dry_run=True,
    )

    assert result.success is False
    assert "Unknown task" in result.message


# ----------------------------------------------------------------
# Scheduler state tests
# ----------------------------------------------------------------


def test_scheduler_state_initialization():
    config = SchedulerConfig()
    states = _build_task_states(config)
    state = SchedulerState(tasks=states)

    assert state.total_runs == 0
    assert state.started_at == 0.0
    assert len(state.tasks) == 4
