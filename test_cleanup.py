from src.archive.cleanup import (
    remove_repository_cache
)


result = remove_repository_cache(
    "AI-Archive/models/Qwen/Qwen3-0.6B/repository"
)


print(
    f"Cache removed: {result}"
)