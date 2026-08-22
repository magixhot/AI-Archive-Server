import logging
import os
import sys


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )

    config_path = os.environ.get(
        "SCHEDULER_CONFIG",
        "config/scheduler.json",
    )

    models_root = os.environ.get(
        "MODELS_ROOT",
        "AI-Archive/models",
    )

    archive_root = os.environ.get(
        "ARCHIVE_ROOT",
        "AI-Archive/models",
    )

    sync_source = os.environ.get(
        "SYNC_SOURCE",
        "AI-Archive/models",
    )

    sync_target = os.environ.get(
        "SYNC_TARGET",
        "AI-Archive/replica",
    )

    from .scheduler import run_scheduler

    run_scheduler(
        config_path,
        models_root=models_root,
        archive_root=archive_root,
        sync_source=sync_source,
        sync_target=sync_target,
    )


if __name__ == "__main__":
    main()
