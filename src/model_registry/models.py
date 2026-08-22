from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ModelRecord:

    model_id: str

    family: Optional[str] = None

    version: Optional[str] = None

    status: str = "QUEUED"

    storage_path: Optional[str] = None

    size_bytes: Optional[int] = None

    sha256: Optional[str] = None

    created_at: Optional[datetime] = None

    verified_at: Optional[datetime] = None

    upstream_revision: Optional[str] = None

    upstream_revision_recorded: Optional[datetime] = None

    metadata_refreshed_at: Optional[datetime] = None