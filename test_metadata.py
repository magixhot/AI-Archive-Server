from src.archive.metadata import (
    write_model_metadata,
    write_files_metadata
)


model_path = (
    "AI-Archive/models/Qwen/Qwen3-0.6B"
)


write_model_metadata(
    model_path,
    {
        "model_id": "Qwen/Qwen3-0.6B",
        "author": "Qwen",
        "sha": "test",
        "private": False,
        "disabled": False
    }
)


write_files_metadata(
    model_path,
    [
        {
            "path": "config.json",
            "size": 12345
        }
    ]
)


print("Metadata created")