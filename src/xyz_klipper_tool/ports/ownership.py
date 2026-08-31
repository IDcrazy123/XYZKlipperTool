"""Typed operation ownership tokens for run, teach, and apply conflicts."""

from dataclasses import dataclass
from enum import Enum


class RunOperation(str, Enum):
    """Mutually exclusive local operation classes."""

    RUN = "run"
    TEACH = "teach"
    APPLY = "apply"


@dataclass(frozen=True)
class RunToken:
    """Opaque owner token; only the issuing lock may release it."""

    operation: RunOperation
    issuer: int
    nonce: int
