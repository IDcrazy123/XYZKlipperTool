"""Immutable corpus inventory and session-separated deterministic splits."""

import hashlib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


@dataclass(frozen=True)
class CorpusEntry:
    """Labeled frame path metadata with immutable content hash and capture session."""

    entry_id: str
    path: Path
    session_id: str
    label: str
    sha256: str

    def __post_init__(self) -> None:
        if not all(
            type(x) is str and x.strip()
            for x in (self.entry_id, self.session_id, self.label, self.sha256)
        ):
            raise ValueError("corpus identity/label/hash required")
        if len(self.sha256) != 64 or any(
            c not in "0123456789abcdef" for c in self.sha256.lower()
        ):
            raise ValueError("invalid corpus hash")


class CorpusSplit(str, Enum):
    """Allowed session-separated corpus partitions."""

    CALIBRATION = "calibration"
    DEVELOPMENT = "development"
    HOLDOUT = "holdout"


def deterministic_split(
    entries: list[CorpusEntry], holdout_ratio: float = 0.2
) -> dict[CorpusSplit, tuple[CorpusEntry, ...]]:
    """Assign whole sessions deterministically; no session appears in multiple splits."""
    if not entries or not 0 < holdout_ratio < 1:
        raise ValueError("invalid corpus split")
    sessions = sorted(
        {entry.session_id for entry in entries},
        key=lambda x: hashlib.sha256(x.encode()).hexdigest(),
    )
    holdout_count = max(1, int(len(sessions) * holdout_ratio))
    holdout = set(sessions[:holdout_count])
    remaining = [s for s in sessions if s not in holdout]
    dev_count = max(1, len(remaining) // 4) if len(remaining) > 1 else 0
    development = set(remaining[:dev_count])
    result: dict[CorpusSplit, list[CorpusEntry]] = {
        CorpusSplit.CALIBRATION: [],
        CorpusSplit.DEVELOPMENT: [],
        CorpusSplit.HOLDOUT: [],
    }
    for entry in sorted(entries, key=lambda x: x.entry_id):
        split = (
            CorpusSplit.HOLDOUT
            if entry.session_id in holdout
            else CorpusSplit.DEVELOPMENT
            if entry.session_id in development
            else CorpusSplit.CALIBRATION
        )
        result[split].append(entry)
    return {key: tuple(value) for key, value in result.items()}
