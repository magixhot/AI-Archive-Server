from src.archive.query import (
    list_models,
    get_model
)


registry = (
    "AI-Archive/registry/models.json"
)


models = list_models(
    registry
)


print(models)


model = get_model(
    registry,
    "Qwen/Qwen3-0.6B"
)


print(model)