import pytest

from repochronicle.domain.bootstrap import (
    BootstrapRun,
    BootstrapState,
    InvalidBootstrapTransition,
    should_enqueue_delta,
)

VALID_SHA = "0123456789abcdef0123456789abcdef01234567"
OTHER_SHA = "abcdef0123456789abcdef0123456789abcdef01"


def test_bootstrap_reaches_ready_only_for_pinned_sha() -> None:
    run = BootstrapRun(source_id="source-1")
    run.transition(BootstrapState.VALIDATING)
    run.pin_target(VALID_SHA)
    run.transition(BootstrapState.QUEUED)
    run.transition(BootstrapState.FETCHING)
    run.transition(BootstrapState.INVENTORYING)
    run.transition(BootstrapState.INDEXING)
    run.transition(BootstrapState.VERIFYING)
    run.record_indexed_sha(VALID_SHA.upper())

    assert run.state is BootstrapState.READY
    assert run.indexed_sha == VALID_SHA
    assert len(run.transitions) == 7


def test_bootstrap_goes_stale_when_remote_moved_during_full_scan() -> None:
    run = BootstrapRun(source_id="source-1")
    run.transition(BootstrapState.VALIDATING)
    run.pin_target(VALID_SHA)
    run.transition(BootstrapState.QUEUED)
    run.transition(BootstrapState.FETCHING)
    run.transition(BootstrapState.INVENTORYING)
    run.transition(BootstrapState.INDEXING)
    run.transition(BootstrapState.VERIFYING)
    run.record_indexed_sha(OTHER_SHA)

    assert run.state is BootstrapState.STALE
    assert run.target_sha == VALID_SHA
    assert run.indexed_sha == OTHER_SHA


def test_invalid_state_transition_is_rejected() -> None:
    run = BootstrapRun(source_id="source-1")
    with pytest.raises(InvalidBootstrapTransition):
        run.transition(BootstrapState.READY)


@pytest.mark.parametrize("sha", ["", "not-a-sha", "1234", "z" * 40])
def test_target_sha_must_be_a_full_hex_object_id(sha: str) -> None:
    run = BootstrapRun(source_id="source-1")
    run.transition(BootstrapState.VALIDATING)
    with pytest.raises(ValueError):
        run.pin_target(sha)


def test_delta_is_queued_only_when_both_revisions_are_known_and_different() -> None:
    assert should_enqueue_delta(VALID_SHA, OTHER_SHA)
    assert not should_enqueue_delta(VALID_SHA, VALID_SHA.upper())
    assert not should_enqueue_delta(None, VALID_SHA)
    assert not should_enqueue_delta(VALID_SHA, None)
