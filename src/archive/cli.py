import argparse
import sys
from pathlib import Path

from .query import (
    list_models,
    get_model,
    count_models,
    list_families,
    find_by_family,
)

from src.storage.validator import (
    validate_structure,
    is_valid,
)

from src.integrity.service import check_integrity

from src.integrity.api import (
    history,
    stats,
)

from src.archive_sync import sync_archive
from src.storage.paths import MODELS_ROOT


def cmd_list():

    models = list_models()

    for model in models:
        print(
            model["id"]
        )


def cmd_count():

    total = count_models()

    print("Models:")
    print(total)


def cmd_families():

    families = list_families()

    for family in families:
        print(
            family
        )


def cmd_family(family):

    models = find_by_family(
        family
    )

    if not models:

        print(
            f"No models found for family: {family}"
        )

        return 1


    for model in models:
        print(
            model["id"]
        )

    return 0


def cmd_info(model_id):

    model = get_model(
        model_id
    )

    if model is None:

        print("ERROR:")
        print(
            f"Model not found: {model_id}"
        )

        return 1


    print("ID:")
    print(model["id"])
    print()

    print("Family:")
    print(model["family"])
    print()

    print("Path:")
    print(model["path"])
    print()

    print("Status:")
    print(model["status"])

    return 0


def cmd_verify(model_id):

    model = get_model(
        model_id
    )

    if model is None:

        print("ERROR:")
        print(
            f"Model not found: {model_id}"
        )

        return 1


    model_path = Path(
        model["path"]
    )


    checks = validate_structure(
        model_path
    )


    print("Model:")
    print(model_id)
    print()


    print("Storage:")
    print(
        "OK"
        if checks["exists"]
        else "FAILED"
    )


    print("Manifest:")
    print(
        "OK"
        if checks["manifest"]
        else "FAILED"
    )


    print("Metadata:")
    print(
        "OK"
        if checks["metadata"]
        else "FAILED"
    )


    print("Repository:")
    print(
        "OK"
        if checks["repository"]
        else "FAILED"
    )


    print()


    integrity = check_integrity(
        model_path
    )


    print("Integrity:")

    print(
        "PASS"
        if integrity.valid
        else "FAILED"
    )

    print()

    print("Files checked:")
    print(
        integrity.checked_files
    )

    print()

    print("Failed files:")
    print(
        len(
            integrity.failed_files
        )
    )

    print()


    if is_valid(checks) and integrity.valid:

        print("Status:")
        print("VALIDATED")

        return 0


    print("Status:")
    print("FAILED")

    return 1


def cmd_history(model_id):

    model = get_model(
        model_id
    )

    if model is None:

        print("ERROR:")
        print(
            f"Model not found: {model_id}"
        )

        return 1


    history_data = history(
        model["id"].split("/")[-1]
    )


    print("Model:")
    print(model_id)
    print()


    print("Integrity History")
    print("-----------------")


    if not history_data:

        print(
            "No integrity history found."
        )

        return 0


    for item in history_data:

        print(
            item["timestamp"]
        )

        print(
            "PASS"
            if item["valid"]
            else "FAILED"
        )

        print(
            f'Checked files: {item["checked_files"]}'
        )

        print(
            f'Failed files: {len(item["failed_files"])}'
        )

        print()


    return 0


def cmd_stats(model_id):

    model = get_model(
        model_id
    )

    if model is None:

        print("ERROR:")
        print(
            f"Model not found: {model_id}"
        )

        return 1


    result = stats(
        model["id"].split("/")[-1]
    )


    print("Model:")
    print(model_id)
    print()


    print("Integrity Statistics")
    print("--------------------")


    print("Total checks:")
    print(
        result["total_checks"]
    )

    print()

    print("Passed:")
    print(
        result["passed"]
    )

    print()

    print("Failed:")
    print(
        result["failed"]
    )

    print()

    print("Success rate:")
    print(
        f'{result["success_rate"]}%'
    )

    print()

    print("Last pass:")
    print(
        result["last_pass"]
    )

    print()

    print("Last fail:")
    print(
        result["last_fail"]
    )

    return 0


def cmd_sync(source, target, apply):

    result = sync_archive(
        source,
        target,
        dry_run=not apply,
    )

    print("Mode:")
    print("APPLY" if apply else "DRY RUN")
    print()

    print("Files to copy:")
    print(len(result.copied_files))
    print()

    print("Unchanged files:")
    print(len(result.unchanged_files))
    print()

    if result.errors:
        print("Errors:")
        for error in result.errors:
            print(error)
        return 1

    return 0


def main():

    parser = argparse.ArgumentParser(
        prog="archive",
        description="Archive CLI - AI Model Archive"
    )


    commands = parser.add_subparsers(
        dest="command",
        required=True
    )


    commands.add_parser(
        "list",
        help="List archived models"
    )


    commands.add_parser(
        "count",
        help="Count archived models"
    )


    commands.add_parser(
        "families",
        help="List model families"
    )


    family = commands.add_parser(
        "family",
        help="List models in family"
    )

    family.add_argument(
        "family",
        help="Model family name"
    )


    info = commands.add_parser(
        "info",
        help="Show model information"
    )

    info.add_argument(
        "model_id",
        help="Model identifier"
    )


    verify = commands.add_parser(
        "verify",
        help="Verify model archive"
    )

    verify.add_argument(
        "model_id",
        help="Model identifier"
    )


    history_parser = commands.add_parser(
        "history",
        help="Show integrity history"
    )

    history_parser.add_argument(
        "model_id",
        help="Model identifier"
    )


    stats_parser = commands.add_parser(
        "stats",
        help="Show integrity statistics"
    )

    stats_parser.add_argument(
        "model_id",
        help="Model identifier"
    )


    sync_parser = commands.add_parser(
        "sync",
        help="Synchronize the archive to a target directory"
    )

    sync_parser.add_argument(
        "target",
        help="Destination archive models directory"
    )

    sync_parser.add_argument(
        "--source",
        default=str(MODELS_ROOT),
        help="Source archive models directory"
    )

    sync_parser.add_argument(
        "--apply",
        action="store_true",
        help="Copy files; without this flag only a synchronization plan is shown"
    )


    args = parser.parse_args()


    if args.command == "list":

        cmd_list()


    elif args.command == "count":

        cmd_count()


    elif args.command == "families":

        cmd_families()


    elif args.command == "family":

        result = cmd_family(
            args.family
        )

        if result:
            sys.exit(result)


    elif args.command == "info":

        result = cmd_info(
            args.model_id
        )

        if result:
            sys.exit(result)


    elif args.command == "verify":

        result = cmd_verify(
            args.model_id
        )

        if result:
            sys.exit(result)


    elif args.command == "history":

        result = cmd_history(
            args.model_id
        )

        if result:
            sys.exit(result)


    elif args.command == "stats":

        result = cmd_stats(
            args.model_id
        )

        if result:
            sys.exit(result)


    elif args.command == "sync":

        result = cmd_sync(
            args.source,
            args.target,
            args.apply,
        )

        if result:
            sys.exit(result)


if __name__ == "__main__":
    main()
