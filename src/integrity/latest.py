from .history_reader import load_history


def latest_result(model: str):
    """
    Return latest integrity result for model.

    Returns:
        dict | None
    """

    history = load_history(
        model
    )

    if not history:
        return None

    return history[-1]