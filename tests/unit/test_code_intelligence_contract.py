from repochronicle.providers.code_intelligence import CodeBackendStatus, CodeEvidence


def test_code_evidence_preserves_revision_provenance() -> None:
    evidence = CodeEvidence(
        source_id="src-1",
        commit_sha="a" * 40,
        path="src/auth.py",
        snippet="def verify_token(): pass",
        score=0.91,
        start_line=12,
        end_line=12,
        symbol_name="verify_token",
        symbol_kind="function",
        backend_id="fixture",
    )

    assert evidence.commit_sha == "a" * 40
    assert evidence.path == "src/auth.py"
    assert evidence.backend_id == "fixture"


def test_backend_status_can_report_missing_or_stale_index() -> None:
    status = CodeBackendStatus(
        backend_id="codesearch",
        available=True,
        indexed_revision="b" * 40,
        detail="index is behind current HEAD",
    )

    assert status.available is True
    assert status.indexed_revision == "b" * 40
    assert "behind" in status.detail
