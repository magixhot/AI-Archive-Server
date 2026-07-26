from src.archive.manifest import create_manifest


manifest = create_manifest(
    "AI-Archive/models/Qwen/Qwen3-0.6B",
    "Qwen/Qwen3-0.6B",
    "Qwen"
)


print(manifest)