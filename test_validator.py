from src.archive.validator import (
    validate_archive
)


result = validate_archive(
    "AI-Archive/models/Qwen/Qwen3-0.6B"
)


print(result)


if all(result.values()):

    print(
        "Archive validation: PASS"
    )

else:

    print(
        "Archive validation: FAILED"
    )