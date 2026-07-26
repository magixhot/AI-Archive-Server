from archive.builder import build_archive


result = build_archive(

    archive_root="AI-Archive",

    model_id="Qwen/Qwen3-0.6B",

    source_repository=
        "test_models/Qwen3-0.6B",


    model_info={

        "model_id":
            "Qwen/Qwen3-0.6B",

        "author":
            "Qwen",

        "version":
            "0.6B",

        "sha":
            "unknown",

        "private":
            False,

        "disabled":
            False

    }

)


print(result)


print(
    "Builder finished"
)


if all(
    result["validation"].values()
):

    print(
        "BUILD SUCCESS"
    )

else:

    print(
        "BUILD FAILED"
    )