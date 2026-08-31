"""Fail-closed deterministic run state machine."""

from dataclasses import dataclass
from enum import Enum


class RunState(str, Enum):
    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class RunReason(str, Enum):
    INVALID_TRANSITION = "INVALID_TRANSITION"
    TERMINAL_STATE = "TERMINAL_STATE"


@dataclass(frozen=True)
class TransitionResult:
    accepted: bool
    previous: RunState
    current: RunState
    reason_code: RunReason | None = None


_TRANSITIONS: dict[RunState, set[RunState]] = {
    RunState.CREATED: {RunState.VALIDATING, RunState.CANCELLED, RunState.FAILED},
    RunState.VALIDATING: {RunState.RUNNING, RunState.CANCELLED, RunState.FAILED},
    RunState.RUNNING: {RunState.COMPLETED, RunState.CANCELLED, RunState.FAILED},
    RunState.COMPLETED: set(),
    RunState.FAILED: set(),
    RunState.CANCELLED: set(),
}


class RunStateMachine:
    """Pure non-blocking state holder; illegal and terminal transitions fail closed."""

    def __init__(self) -> None:
        self._state = RunState.CREATED

    @property
    def state(self) -> RunState:
        return self._state

    def transition(self, target: RunState) -> TransitionResult:
        """Attempt a transition without I/O; invalid requests leave state unchanged."""
        previous = self._state
        if target not in _TRANSITIONS[previous]:
            reason = (
                RunReason.TERMINAL_STATE
                if not _TRANSITIONS[previous]
                else RunReason.INVALID_TRANSITION
            )
            return TransitionResult(False, previous, previous, reason)
        self._state = target
        return TransitionResult(True, previous, target)
