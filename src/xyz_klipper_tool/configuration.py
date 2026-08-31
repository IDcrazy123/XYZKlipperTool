"""Deterministic, secret-redacting configuration identity."""

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

_SECRET_WORDS = ("password", "secret", "token", "api_key", "apikey", "credential")


def _normalize(value: object, path: str = "") -> object:
    if isinstance(value, Mapping):
        mapping = cast(Mapping[object, object], value)
        if any(type(key) is not str for key in mapping):
            raise ValueError(f"configuration keys must be strings at {path}")
        return {
            key: "<redacted>"
            if any(word in str(key).lower() for word in _SECRET_WORDS)
            else _normalize(item, f"{path}.{key}")
            for key, item in sorted(mapping.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [
            _normalize(item, f"{path}[]")
            for item in cast(list[object] | tuple[object, ...], value)
        ]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise ValueError(f"unsupported configuration value at {path}")


@dataclass(frozen=True)
class ConfigurationFingerprint:
    """Versioned SHA-256 identity of canonical redacted config; no I/O or secrets are retained."""

    version: int
    digest: str
    canonical_json: str

    def __post_init__(self) -> None:
        if (
            type(self.version) is not int
            or self.version != 1
            or len(self.digest) != 64
            or any(c not in "0123456789abcdef" for c in self.digest)
        ):
            raise ValueError("unsupported or malformed fingerprint")
        expected = hashlib.sha256(self.canonical_json.encode("utf-8")).hexdigest()
        if self.digest != expected:
            raise ValueError("fingerprint digest does not match canonical JSON")


def fingerprint(configuration: Mapping[str, object]) -> ConfigurationFingerprint:
    """Canonicalize and hash configuration with stable key order and redacted secret fields."""
    normalized = _normalize(configuration)
    canonical = json.dumps(
        normalized,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return ConfigurationFingerprint(1, digest, canonical)
