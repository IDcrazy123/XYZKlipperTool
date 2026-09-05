"""Versioned, path-confined frame inventory and session-separated corpus splits."""

import hashlib
import json
import math
import random
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class CorpusSplit(str, Enum):
    """Allowed whole-session corpus partitions."""

    CALIBRATION = "calibration"
    DEVELOPMENT = "development"
    HOLDOUT = "holdout"


@dataclass(frozen=True)
class CorpusEntry:
    """Bounded labeled frame record with relative path and immutable content hash."""

    entry_id: str
    path: Path
    session_id: str
    label: str
    sha256: str
    provenance: str = "SYNTHETIC"
    expected_candidate_count: int = 0
    expected_center_px: tuple[float, float] | None = None
    failure_class: str | None = None
    byte_size: int = 0

    def __post_init__(self) -> None:
        for value in (self.entry_id, self.session_id, self.label, self.sha256):
            if type(value) is not str or not value.strip() or len(value) > 128:
                raise ValueError("corpus identity/label/hash required")
        if len(self.sha256) != 64 or any(
            c not in "0123456789abcdef" for c in self.sha256
        ):
            raise ValueError("invalid corpus hash")
        if self.provenance not in ("SYNTHETIC", "REAL_SANITIZED"):
            raise ValueError("unsupported corpus provenance")
        path_object: Any = self.path
        if (
            not isinstance(path_object, Path)
            or self.path.is_absolute()
            or ".." in self.path.parts
        ):
            raise ValueError("corpus path must be relative and confined")
        if (
            type(self.expected_candidate_count) is not int
            or not 0 <= self.expected_candidate_count <= 100
        ):
            raise ValueError("candidate count out of bounds")
        if self.expected_center_px is not None and (
            len(self.expected_center_px) != 2
            or any(
                type(v) is not float or not math.isfinite(v) or v < 0
                for v in self.expected_center_px
            )
        ):
            raise ValueError("center must be finite nonnegative pixel floats")
        if self.failure_class is not None and (
            type(self.failure_class) is not str or len(self.failure_class) > 128
        ):
            raise ValueError("failure class out of bounds")
        if (
            type(self.byte_size) is not int
            or not 0 <= self.byte_size <= 64 * 1024 * 1024
        ):
            raise ValueError("frame byte size out of bounds")


def build_inventory(
    root: Path, paths: list[Path], provenance: str = "SYNTHETIC"
) -> tuple[CorpusEntry, ...]:
    """Build a deterministic relative-path inventory without leaking absolute paths."""
    resolved_root = root.resolve()
    if type(paths) is not list or len(paths) > 10000:
        raise ValueError("corpus file count out of bounds")
    entries: list[CorpusEntry] = []
    for path in sorted(paths, key=lambda item: str(item)):
        resolved = path.resolve()
        if resolved != resolved_root and resolved_root not in resolved.parents:
            raise ValueError("corpus path escapes root")
        relative = resolved.relative_to(resolved_root)
        data = resolved.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        entry_id = hashlib.sha256(str(relative).encode()).hexdigest()[:32]
        session_id = relative.parts[0] if relative.parts else "session"
        entries.append(
            CorpusEntry(
                entry_id,
                relative,
                session_id,
                "UNLABELED",
                digest,
                provenance,
                0,
                None,
                "UNLABELED",
                len(data),
            )
        )
    verify_inventory(root, entries)
    return tuple(entries)


def verify_inventory(
    root: Path, entries: tuple[CorpusEntry, ...] | list[CorpusEntry]
) -> None:
    """Recompute confined file hashes and reject duplicate or mismatched records."""
    root_resolved = root.resolve()
    ids: set[str] = set()
    paths: set[Path] = set()
    for entry in entries:
        if entry.entry_id in ids or entry.path in paths:
            raise ValueError("duplicate corpus identity/path")
        ids.add(entry.entry_id)
        paths.add(entry.path)
        resolved = (root_resolved / entry.path).resolve()
        if resolved != root_resolved and root_resolved not in resolved.parents:
            raise ValueError("corpus path escapes root")
        data = resolved.read_bytes()
        if (
            len(data) != entry.byte_size
            or hashlib.sha256(data).hexdigest() != entry.sha256
        ):
            raise ValueError("corpus hash or byte-size mismatch")


def inventory_json(entries: tuple[CorpusEntry, ...] | list[CorpusEntry]) -> str:
    """Serialize only relative, non-private inventory data deterministically."""
    verify = sorted(entries, key=lambda item: item.entry_id)
    return json.dumps(
        {
            "schema_version": 1,
            "entries": [
                entry.__dict__
                | {
                    "path": str(entry.path),
                    "expected_center_px": entry.expected_center_px,
                }
                for entry in verify
            ],
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def deterministic_split(
    entries: list[CorpusEntry],
    holdout_ratio: float = 0.2,
    development_ratio: float = 0.2,
    seed: int = 0,
) -> dict[CorpusSplit, tuple[CorpusEntry, ...]]:
    """Assign whole sessions deterministically with three nonempty partitions."""
    if (
        not entries
        or not 0 < holdout_ratio < 1
        or not 0 < development_ratio < 1
        or holdout_ratio + development_ratio >= 1
        or type(seed) is not int
    ):
        raise ValueError("invalid corpus split configuration")
    sessions = sorted({entry.session_id for entry in entries})
    if len(sessions) < 3:
        raise ValueError("at least three sessions are required")
    random.Random(seed).shuffle(sessions)
    holdout_count = max(1, round(len(sessions) * holdout_ratio))
    development_count = max(1, round(len(sessions) * development_ratio))
    if holdout_count + development_count >= len(sessions):
        raise ValueError("split ratios leave no calibration session")
    holdout = set(sessions[:holdout_count])
    development = set(sessions[holdout_count : holdout_count + development_count])
    result: dict[CorpusSplit, list[CorpusEntry]] = {
        CorpusSplit.CALIBRATION: [],
        CorpusSplit.DEVELOPMENT: [],
        CorpusSplit.HOLDOUT: [],
    }
    for entry in sorted(entries, key=lambda item: item.entry_id):
        key = (
            CorpusSplit.HOLDOUT
            if entry.session_id in holdout
            else CorpusSplit.DEVELOPMENT
            if entry.session_id in development
            else CorpusSplit.CALIBRATION
        )
        result[key].append(entry)
    return {key: tuple(value) for key, value in result.items()}


def evaluate_benchmark(
    holdout: tuple[CorpusEntry, ...],
    runners: dict[
        str, Callable[[CorpusEntry], tuple[int, tuple[float, float] | None, str]]
    ],
) -> dict[str, dict[str, object]]:
    """Evaluate injected runners on labeled holdout entries only.

    Each runner returns predicted candidate count, optional predicted center in
    pixels, and a reason string. Center error is computed here from ground truth;
    runner-supplied error values are never trusted. This publishes offline metrics only; it never
    creates or claims real camera evidence.
    """
    if not holdout:
        raise ValueError("bounded labeled holdout is required")
    for entry in holdout:
        if entry.label == "UNLABELED" or entry.failure_class == "UNLABELED":
            raise ValueError("unlabeled entries are forbidden in benchmark holdout")
        if entry.expected_candidate_count > 0 and entry.expected_center_px is None:
            raise ValueError("positive holdout entries require a labeled center")
        if entry.expected_candidate_count == 0 and entry.expected_center_px is not None:
            raise ValueError("negative holdout entries cannot carry a labeled center")
    output: dict[str, dict[str, object]] = {}
    for name, runner in sorted(runners.items()):
        rows = [runner(entry) for entry in holdout]
        tp = sum(
            row[0] > 0 and entry.expected_candidate_count > 0
            for row, entry in zip(rows, holdout)
        )
        fp = sum(
            row[0] > 0 and entry.expected_candidate_count == 0
            for row, entry in zip(rows, holdout)
        )
        fn = sum(
            row[0] == 0 and entry.expected_candidate_count > 0
            for row, entry in zip(rows, holdout)
        )
        tn = sum(
            row[0] == 0 and entry.expected_candidate_count == 0
            for row, entry in zip(rows, holdout)
        )
        errors = [
            math.hypot(
                row[1][0] - entry.expected_center_px[0],
                row[1][1] - entry.expected_center_px[1],
            )
            for row, entry in zip(rows, holdout)
            if row[1] is not None and entry.expected_center_px is not None
        ]
        positive_denominator = tp + fp
        recall_denominator = tp + fn
        output[name] = {
            "dataset_label": "SYNTHETIC"
            if all(entry.provenance == "SYNTHETIC" for entry in holdout)
            else "REAL_SANITIZED",
            "samples": len(rows),
            "true_positive": tp,
            "false_positive": fp,
            "false_negative": fn,
            "true_negative": tn,
            "precision": tp / positive_denominator if positive_denominator else 0.0,
            "recall": tp / recall_denominator if recall_denominator else 0.0,
            "center_error_px_mean": sum(errors) / max(1, len(errors)),
            "center_error_px_median": sorted(errors)[len(errors) // 2]
            if errors
            else 0.0,
            "center_error_px_max": max(errors, default=0.0),
            "failure_classes": sorted({row[2] for row in rows if row[2]}),
        }
    return output
