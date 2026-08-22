from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .config import SchedulerConfig, load_config
from .tasks import TaskResult

logger = logging.getLogger(__name__)


@dataclass
class TaskState:
    name: str
    interval_seconds: int
    enabled: bool
    last_run: float = 0.0
    consecutive_failures: int = 0


@dataclass
class SchedulerState:
    tasks: dict[str, TaskState] = field(default_factory=dict)
    started_at: float = 0.0
    total_runs: int = 0


def _build_task_states(
    config: SchedulerConfig,
) -> dict[str, TaskState]:
    tasks: dict[str, TaskState] = {}

    tasks["integrity_check"] = TaskState(
        name="integrity_check",
        interval_seconds=config.integrity_check.interval_seconds,
        enabled=config.integrity_check.enabled,
    )

    tasks["reconciliation"] = TaskState(
        name="reconciliation",
        interval_seconds=config.reconciliation.interval_seconds,
        enabled=config.reconciliation.enabled,
    )

    tasks["archive_sync"] = TaskState(
        name="archive_sync",
        interval_seconds=config.archive_sync.interval_seconds,
        enabled=config.archive_sync.enabled,
    )

    return tasks


def _is_due(
    task_state: TaskState,
    now: float,
) -> bool:
    if not task_state.enabled:
        return False

    elapsed = now - task_state.last_run
    return elapsed >= task_state.interval_seconds


def run_scheduler(
    config_path: str | Path | None = None,
    *,
    models_root: str | Path = "AI-Archive/models",
    archive_root: str | Path = "AI-Archive/models",
    sync_source: str | Path = "AI-Archive/models",
    sync_target: str | Path = "AI-Archive/replica",
    _sleep_fn: Callable[[float], None] | None = None,
) -> None:
    config = load_config(config_path)
    state = SchedulerState(
        tasks=_build_task_states(config),
        started_at=time.time(),
    )

    sleep_fn = _sleep_fn or time.sleep

    archive_sync_dry_run = config.archive_sync.dry_run

    logger.info(
        "Scheduler started with tasks: %s",
        {
            name: {
                "enabled": ts.enabled,
                "interval_seconds": ts.interval_seconds,
            }
            for name, ts in state.tasks.items()
        },
    )

    while True:
        now = time.time()

        for name, task_state in state.tasks.items():
            if not _is_due(task_state, now):
                continue

            logger.info("Running task: %s", name)
            task_state.last_run = now
            state.total_runs += 1

            try:
                result = _run_task(
                    name,
                    models_root=models_root,
                    archive_root=archive_root,
                    sync_source=sync_source,
                    sync_target=sync_target,
                    dry_run=archive_sync_dry_run,
                )

                if result.success:
                    task_state.consecutive_failures = 0
                    logger.info(
                        "Task %s completed: %s",
                        name,
                        result.message,
                    )
                else:
                    task_state.consecutive_failures += 1
                    logger.warning(
                        "Task %s failed (%d consecutive): %s",
                        name,
                        task_state.consecutive_failures,
                        result.message,
                    )
            except Exception as exc:
                task_state.consecutive_failures += 1
                logger.error(
                    "Task %s exception (%d consecutive): %s",
                    name,
                    task_state.consecutive_failures,
                    exc,
                )

        sleep_fn(10)


def _run_task(
    task_name: str,
    *,
    models_root: str | Path,
    archive_root: str | Path,
    sync_source: str | Path,
    sync_target: str | Path,
    dry_run: bool,
) -> TaskResult:
    from .tasks import (
        run_archive_sync,
        run_integrity_check,
        run_reconciliation,
    )

    if task_name == "integrity_check":
        return run_integrity_check(models_root)

    if task_name == "reconciliation":
        return run_reconciliation(archive_root)

    if task_name == "archive_sync":
        return run_archive_sync(
            sync_source,
            sync_target,
            dry_run=dry_run,
        )

    return TaskResult(
        task_name=task_name,
        success=False,
        message=f"Unknown task: {task_name}",
    )
