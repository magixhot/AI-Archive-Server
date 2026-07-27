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

from storage.validator import (
    validate_structure,
    is_valid,
)

from integrity.service import check_integrity



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
            sys.exit(
                result
            )



    elif args.command == "info":

        result = cmd_info(
            args.model_id
        )

        if result:
            sys.exit(
                result
            )



    elif args.command == "verify":

        result = cmd_verify(
            args.model_id
        )

        if result:
            sys.exit(
                result
            )