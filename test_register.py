from src.archive.registry import (
    register_model
)


model = register_model(

    "AI-Archive/registry/models.json",

    "Qwen/Qwen3-0.6B",

    "models/Qwen/Qwen3-0.6B",

    "Qwen"

)


print(
    model
)

print(
    "Model registered"
)