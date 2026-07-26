from src.archive.file_index import (
    generate_file_index
)


files = generate_file_index(

    "AI-Archive/models/Qwen/Qwen3-0.6B/repository",

    "AI-Archive/models/Qwen/Qwen3-0.6B/metadata/files.json"

)


print(
    f"Indexed files: {len(files)}"
)