import pytest

from repochronicle.domain.evidence import Evidence, select_evidence


def test_evidence_selection_respects_budget_and_sorts_by_score() -> None:
    pack = select_evidence(
        [
            Evidence("low", "low evidence", 0.1, "https://example.test/low", citation="L"),
            Evidence("high", "high", 0.9, "https://example.test/high", citation="H"),
            Evidence("mid", "medium", 0.5, "https://example.test/mid", citation="M"),
        ],
        budget_chars=12,
    )

    assert [item.evidence_id for item in pack.items] == ["high", "mid"]
    assert pack.used_chars == 12
    assert pack.omitted_count == 1


def test_duplicate_evidence_keeps_highest_score() -> None:
    pack = select_evidence(
        [
            Evidence("same", "old", 0.1, "https://example.test/a"),
            Evidence("same", "new", 0.9, "https://example.test/a"),
        ],
        budget_chars=100,
    )

    assert len(pack.items) == 1
    assert pack.items[0].text == "new"


def test_negative_budget_is_rejected() -> None:
    with pytest.raises(ValueError):
        select_evidence([], -1)
