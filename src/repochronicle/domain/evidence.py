"""Evidence selection with a strict, deterministic character budget."""

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Evidence:
    evidence_id: str
    text: str
    score: float
    source_url: str
    source_kind: str = "unknown"
    citation: str = ""


@dataclass(frozen=True, slots=True)
class EvidencePack:
    items: tuple[Evidence, ...]
    used_chars: int
    budget_chars: int
    omitted_count: int


def select_evidence(items: Sequence[Evidence], budget_chars: int) -> EvidencePack:
    """Select highest-scoring unique evidence without exceeding a character budget.

    `budget_chars` is a scaffold-level guardrail; production must also use the active
    model tokenizer and reserve room for instructions, history, tool schemas, and the answer.
    """
    if budget_chars < 0:
        raise ValueError("budget_chars must be non-negative")

    unique: dict[str, Evidence] = {}
    for item in items:
        current = unique.get(item.evidence_id)
        if current is None or item.score > current.score:
            unique[item.evidence_id] = item

    ranked = sorted(unique.values(), key=lambda item: (-item.score, item.evidence_id))
    selected: list[Evidence] = []
    used = 0
    for item in ranked:
        cost = len(item.text) + len(item.citation)
        if cost <= budget_chars - used:
            selected.append(item)
            used += cost

    return EvidencePack(
        items=tuple(selected),
        used_chars=used,
        budget_chars=budget_chars,
        omitted_count=len(ranked) - len(selected),
    )
