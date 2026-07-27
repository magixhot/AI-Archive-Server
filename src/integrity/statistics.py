from .history_reader import load_history


def get_statistics(model: str) -> dict:
    """
    Calculate integrity statistics for a model.
    """

    history = load_history(model)

    if not history:

        return {
            "model": model,
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
            "success_rate": 0.0,
            "last_pass": None,
            "last_fail": None,
        }

    total = len(history)

    passed = sum(
        1
        for item in history
        if item["valid"]
    )

    failed = total - passed

    last_pass = None
    last_fail = None

    for item in reversed(history):

        if item["valid"] and last_pass is None:

            last_pass = item["timestamp"]

        if (not item["valid"]) and last_fail is None:

            last_fail = item["timestamp"]

        if (
            last_pass is not None
            and last_fail is not None
        ):
            break

    return {
        "model": model,
        "total_checks": total,
        "passed": passed,
        "failed": failed,
        "success_rate": round(
            passed / total * 100,
            2,
        ),
        "last_pass": last_pass,
        "last_fail": last_fail,
    }