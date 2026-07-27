from pathlib import Path
from .statistics import get_statistics
from .service import check_integrity
from .history_reader import load_history
from .latest import latest_result


def check(model_path: str | Path):
    """
    Run integrity check.

    Returns:
        IntegrityResult
    """

    return check_integrity(
        model_path
    )


def history(model: str):
    """
    Return integrity history.

    Returns:
        list[dict]
    """

    return load_history(
        model
    )


def latest(model: str):
    """
    Return latest integrity result.

    Returns:
        dict | None
    """

    return latest_result(
        model
    )

def stats(model: str) -> dict:
    """
    Return integrity statistics.
    """

    return get_statistics(
        model
    )    