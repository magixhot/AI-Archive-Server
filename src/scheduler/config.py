from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


DEFAULT_CONFIG_PATH = Path("config/scheduler.json")

DEFAULT_INTEGRITY_INTERVAL = 86400
DEFAULT_RECONCILIATION_INTERVAL = 21600
DEFAULT_ARCHIVE_SYNC_INTERVAL = 86400
DEFAULT_METADATA_REFRESH_INTERVAL = 86400


@dataclass
class TaskConfig:
    enabled: bool = True
    interval_seconds: int = 86400


@dataclass
class ArchiveSyncConfig(TaskConfig):
    dry_run: bool = True


@dataclass
class SchedulerConfig:
    integrity_check: TaskConfig = field(
        default_factory=lambda: TaskConfig(
            enabled=True,
            interval_seconds=DEFAULT_INTEGRITY_INTERVAL,
        )
    )
    reconciliation: TaskConfig = field(
        default_factory=lambda: TaskConfig(
            enabled=True,
            interval_seconds=DEFAULT_RECONCILIATION_INTERVAL,
        )
    )
    archive_sync: ArchiveSyncConfig = field(
        default_factory=lambda: ArchiveSyncConfig(
            enabled=True,
            interval_seconds=DEFAULT_ARCHIVE_SYNC_INTERVAL,
            dry_run=True,
        )
    )
    metadata_refresh: TaskConfig = field(
        default_factory=lambda: TaskConfig(
            enabled=True,
            interval_seconds=DEFAULT_METADATA_REFRESH_INTERVAL,
        )
    )


def load_config(
    config_path: str | Path | None = None,
) -> SchedulerConfig:
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH

    if not path.exists():
        logger.info(
            "No scheduler config at %s, using defaults",
            path,
        )
        return SchedulerConfig()

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning(
            "Failed to load scheduler config from %s: %s. Using defaults.",
            path,
            exc,
        )
        return SchedulerConfig()

    tasks = raw.get("tasks", {})

    config = SchedulerConfig()

    if "integrity_check" in tasks:
        tc = tasks["integrity_check"]
        config.integrity_check = TaskConfig(
            enabled=tc.get("enabled", True),
            interval_seconds=tc.get(
                "interval_seconds",
                DEFAULT_INTEGRITY_INTERVAL,
            ),
        )

    if "reconciliation" in tasks:
        tc = tasks["reconciliation"]
        config.reconciliation = TaskConfig(
            enabled=tc.get("enabled", True),
            interval_seconds=tc.get(
                "interval_seconds",
                DEFAULT_RECONCILIATION_INTERVAL,
            ),
        )

    if "archive_sync" in tasks:
        tc = tasks["archive_sync"]
        config.archive_sync = ArchiveSyncConfig(
            enabled=tc.get("enabled", True),
            interval_seconds=tc.get(
                "interval_seconds",
                DEFAULT_ARCHIVE_SYNC_INTERVAL,
            ),
            dry_run=tc.get("dry_run", True),
        )

    if "metadata_refresh" in tasks:
        tc = tasks["metadata_refresh"]
        config.metadata_refresh = TaskConfig(
            enabled=tc.get("enabled", True),
            interval_seconds=tc.get(
                "interval_seconds",
                DEFAULT_METADATA_REFRESH_INTERVAL,
            ),
        )

    return config
