from src.archive.query import (
    list_models,
    get_model,
    count_models,
    list_families,
    find_by_family
)


registry = (
    "AI-Archive/registry/models.json"
)


print(
    "MODELS:"
)

print(
    list_models(registry)
)


print(
    "COUNT:"
)

print(
    count_models(registry)
)


print(
    "FAMILIES:"
)

print(
    list_families(registry)
)


print(
    "QWEN:"
)

print(
    find_by_family(
        registry,
        "Qwen"
    )
)


print(
    "MODEL:"
)

print(
    get_model(
        registry,
        "Qwen/Qwen3-0.6B"
    )
)