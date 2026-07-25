from enum import Enum


class ModelStatus(str, Enum):

    QUEUED = "QUEUED"

    DOWNLOADING = "DOWNLOADING"

    DOWNLOADED = "DOWNLOADED"

    VERIFYING = "VERIFYING"

    VERIFIED = "VERIFIED"

    ARCHIVED = "ARCHIVED"

    FAILED = "FAILED"