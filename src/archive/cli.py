import argparse
import sys

from .query import (
    list_models,
    get_model,
    count_models,
    list_families,
    find_by_family
)


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

        print(
            "ERROR:"
        )

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