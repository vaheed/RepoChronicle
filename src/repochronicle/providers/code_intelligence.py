"""Replaceable contract for out-of-process code intelligence engines."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class CodeEvidence:
    """A code result tied to an immutable source revision."""

    source_id: str
    commit_sha: str
    path: str
    snippet: str
    score: float
    start_line: int | None = None
    end_line: int | None = None
    symbol_name: str | None = None
    symbol_kind: str | None = None
    backend_id: str = "unknown"


@dataclass(frozen=True, slots=True)
class CodeBackendStatus:
    backend_id: str
    available: bool
    indexed_revision: str | None = None
    detail: str = ""


class CodeIntelligenceBackend(Protocol):
    """Adapter boundary for CodeGraph, codesearch, or another compatible engine."""

    @property
    def backend_id(self) -> str: ...

    async def search(
        self,
        *,
        query: str,
        source_ids: Sequence[str],
        limit: int,
    ) -> Sequence[CodeEvidence]: ...

    async def get_symbol(
        self,
        *,
        source_id: str,
        commit_sha: str,
        symbol_name: str,
    ) -> Sequence[CodeEvidence]: ...

    async def change_impact(
        self,
        *,
        source_id: str,
        commit_sha: str,
        changed_paths: Sequence[str],
        limit: int,
    ) -> Sequence[CodeEvidence]: ...

    async def status(self, *, source_id: str) -> CodeBackendStatus: ...
