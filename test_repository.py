from src.archive.repository import copy_repository


result = copy_repository(
    "test_models/Qwen3-0.6B",
    "AI-Archive/models/Qwen/Qwen3-0.6B/repository"
)


print(
    f"Repository copied: {result}"
)