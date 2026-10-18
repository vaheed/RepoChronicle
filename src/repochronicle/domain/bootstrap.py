"""Bootstrap state machine for first-time source initialization."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class BootstrapState(StrEnum):
    REGISTERED = "registered"
    VALIDATING = "validating"
    QUEUED = "queued"
    FETCHING = "fetching"
    INVENTORYING = "inventorying"
    INDEXING = "indexing"
    EMBEDDING = "embedding"
    BACKFILLING_ACTIVITY = "backfilling_activity"
    VERIFYING = "verifying"
    READY = "ready"
    STALE = "stale"
    RETRYING = "retrying"
    FAILED = "failed"
    DISABLED = "disabled"
    PERMISSION_LIMITED = "permission_limited"


_ALLOWED_TRANSITIONS: dict[BootstrapState, set[BootstrapState]] = {
    BootstrapState.REGISTERED: {BootstrapState.VALIDATING, BootstrapState.DISABLED},
    BootstrapState.VALIDATING: {
        BootstrapState.QUEUED,
        BootstrapState.PERMISSION_LIMITED,
        BootstrapState.FAILED,
    },
    BootstrapState.QUEUED: {BootstrapState.FETCHING, BootstrapState.DISABLED},
    BootstrapState.FETCHING: {
        BootstrapState.INVENTORYING,
        BootstrapState.RETRYING,
        BootstrapState.FAILED,
    },
    BootstrapState.INVENTORYING: {
        BootstrapState.INDEXING,
        BootstrapState.RETRYING,
        BootstrapState.FAILED,
    },
    BootstrapState.INDEXING: {
        BootstrapState.EMBEDDING,
        BootstrapState.BACKFILLING_ACTIVITY,
        BootstrapState.VERIFYING,
        BootstrapState.RETRYING,
        BootstrapState.FAILED,
    },
    BootstrapState.EMBEDDING: {
        BootstrapState.BACKFILLING_ACTIVITY,
        BootstrapState.VERIFYING,
        BootstrapState.RETRYING,
        BootstrapState.FAILED,
    },
    BootstrapState.BACKFILLING_ACTIVITY: {
        BootstrapState.VERIFYING,
        BootstrapState.RETRYING,
        BootstrapState.FAILED,
    },
    BootstrapState.VERIFYING: {
        BootstrapState.READY,
        BootstrapState.STALE,
        BootstrapState.RETRYING,
        BootstrapState.FAILED,
    },
    BootstrapState.READY: {BootstrapState.STALE, BootstrapState.DISABLED},
    BootstrapState.STALE: {BootstrapState.QUEUED, BootstrapState.FETCHING, BootstrapState.DISABLED},
    BootstrapState.RETRYING: {
        BootstrapState.FETCHING,
        BootstrapState.INVENTORYING,
        BootstrapState.INDEXING,
        BootstrapState.EMBEDDING,
        BootstrapState.BACKFILLING_ACTIVITY,
        BootstrapState.VERIFYING,
        BootstrapState.FAILED,
        BootstrapState.DISABLED,
    },
    BootstrapState.PERMISSION_LIMITED: {BootstrapState.VALIDATING, BootstrapState.DISABLED},
    BootstrapState.FAILED: {
        BootstrapState.VALIDATING,
        BootstrapState.QUEUED,
        BootstrapState.DISABLED,
    },
    BootstrapState.DISABLED: {BootstrapState.REGISTERED},
}


class InvalidBootstrapTransition(ValueError):
    """Raised when a source tries to enter a disallowed state."""


@dataclass(slots=True)
class BootstrapRun:
    source_id: str
    state: BootstrapState = BootstrapState.REGISTERED
    target_sha: str | None = None
    indexed_sha: str | None = None
    checkpoint: str | None = None
    error_category: str | None = None
    transitions: list[tuple[BootstrapState, datetime]] = field(default_factory=list)

    def transition(self, next_state: BootstrapState, *, error_category: str | None = None) -> None:
        if next_state not in _ALLOWED_TRANSITIONS[self.state]:
            raise InvalidBootstrapTransition(
                f"Transition {self.state.value} -> {next_state.value} is not allowed"
            )
        self.state = next_state
        self.error_category = error_category
        self.transitions.append((next_state, datetime.now(UTC)))

    def pin_target(self, sha: str) -> None:
        if self.state not in {
            BootstrapState.VALIDATING,
            BootstrapState.QUEUED,
            BootstrapState.FETCHING,
        }:
            raise InvalidBootstrapTransition(
                "A target SHA can only be pinned during validation or fetch"
            )
        if (
            not sha
            or len(sha) not in {40, 64}
            or any(char not in "0123456789abcdefABCDEF" for char in sha)
        ):
            raise ValueError("target SHA must be a full hexadecimal Git object ID")
        self.target_sha = sha.lower()

    def record_indexed_sha(self, sha: str) -> None:
        if self.state != BootstrapState.VERIFYING:
            raise InvalidBootstrapTransition(
                "The indexed SHA may only be finalized while verifying"
            )
        self.indexed_sha = sha.lower()
        if self.target_sha != self.indexed_sha:
            self.transition(BootstrapState.STALE)
        else:
            self.transition(BootstrapState.READY)


def should_enqueue_delta(indexed_sha: str | None, remote_sha: str | None) -> bool:
    """Return true if a known current remote revision differs from the indexed revision."""
    return bool(indexed_sha and remote_sha and indexed_sha.lower() != remote_sha.lower())
