"""Normalized chat event schema shared by platform adapters."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class NormalizedMessage:
    platform: str
    source_id: str
    external_message_id: str
    external_channel_id: str
    external_author_id: str | None
    body: str
    created_at: datetime
    reply_to_message_id: str | None = None
    thread_id: str | None = None
    edited_at: datetime | None = None
    source_url: str | None = None
    is_bot: bool = False
    is_deleted: bool = False
