from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class UpstreamProvenance:
    model_id: str
    upstream_provider: str
    upstream_revision: str | None = None
    upstream_url: str | None = None
    declared_revision: str | None = None
    recorded_at: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> UpstreamProvenance:
        return cls(
            model_id=data.get("model_id", ""),
            upstream_provider=data.get(
                "upstream_provider", "huggingface"
            ),
            upstream_revision=data.get(
                "upstream_revision"
            ),
            upstream_url=data.get("upstream_url"),
            declared_revision=data.get(
                "declared_revision"
            ),
            recorded_at=data.get("recorded_at"),
        )


@dataclass
class RefreshResult:
    model_id: str
    provenance_changed: bool
    upstream_changed: bool
    upstream_revision: str | None
    previous_revision: str | None
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


def _provenance_path(
    model_path: str | Path,
) -> Path:
    return Path(model_path) / "metadata" / "provenance.json"


def read_provenance(
    model_path: str | Path,
) -> UpstreamProvenance | None:
    path = _provenance_path(model_path)

    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return UpstreamProvenance.from_dict(data)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning(
            "Failed to read provenance from %s: %s",
            path,
            exc,
        )
        return None


def write_provenance(
    model_path: str | Path,
    provenance: UpstreamProvenance,
) -> Path:
    path = _provenance_path(model_path)

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            provenance.to_dict(),
            f,
            indent=2,
            ensure_ascii=False,
        )

    return path


def _resolve_upstream_info(
    model_id: str,
) -> UpstreamProvenance | None:
    try:
        from src.hf_client.client import get_model_info

        info = get_model_info(model_id)

        upstream_url = (
            f"https://huggingface.co/{model_id}"
        )

        return UpstreamProvenance(
            model_id=model_id,
            upstream_provider="huggingface",
            upstream_revision=info.sha,
            upstream_url=upstream_url,
            declared_revision=None,
            recorded_at=(
                datetime.now(timezone.utc)
                .isoformat()
            ),
        )
    except Exception as exc:
        logger.warning(
            "Failed to resolve upstream info for %s: %s",
            model_id,
            exc,
        )
        return None


def refresh_metadata(
    model_id: str,
    model_path: str | Path,
) -> RefreshResult:
    model_path = Path(model_path)

    existing = read_provenance(model_path)

    previous_revision = (
        existing.upstream_revision
        if existing
        else None
    )

    upstream = _resolve_upstream_info(model_id)

    if upstream is None:
        return RefreshResult(
            model_id=model_id,
            provenance_changed=False,
            upstream_changed=False,
            upstream_revision=previous_revision,
            previous_revision=previous_revision,
            message=(
                f"Upstream unavailable for {model_id}"
            ),
        )

    upstream_changed = (
        previous_revision is not None
        and upstream.upstream_revision
        != previous_revision
    )

    provenance_changed = (
        existing is None
        or upstream.upstream_revision
        != previous_revision
        or upstream.recorded_at
        != existing.recorded_at
    )

    write_provenance(model_path, upstream)

    if existing is None:
        msg = (
            f"Provenance created for {model_id}: "
            f"revision={upstream.upstream_revision}"
        )
    elif upstream_changed:
        msg = (
            f"Upstream changed for {model_id}: "
            f"{previous_revision} -> "
            f"{upstream.upstream_revision}"
        )
    else:
        msg = (
            f"Provenance refreshed for {model_id}: "
            f"revision unchanged "
            f"({upstream.upstream_revision})"
        )

    return RefreshResult(
        model_id=model_id,
        provenance_changed=provenance_changed,
        upstream_changed=upstream_changed,
        upstream_revision=upstream.upstream_revision,
        previous_revision=previous_revision,
        message=msg,
    )
