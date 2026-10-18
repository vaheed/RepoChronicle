"""Discord event normalization (gateway client is introduced in F5)."""

from datetime import UTC, datetime
from typing import Any

from repochronicle.connectors.events import NormalizedMessage


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(UTC)


def normalize_discord_message(
    message: dict[str, Any], *, source_id: str
) -> NormalizedMessage | None:
    message_id = message.get("id")
    channel_id = message.get("channel_id")
    created_at = _parse_timestamp(message.get("timestamp"))
    if message_id is None or channel_id is None or created_at is None:
        return None
    author = message.get("author") or {}
    guild_id = message.get("guild_id")
    thread = message.get("thread") or {}
    thread_id = thread.get("id") or message.get("thread_id")
    return NormalizedMessage(
        platform="discord",
        source_id=source_id,
        external_message_id=str(message_id),
        external_channel_id=str(channel_id),
        external_author_id=str(author["id"]) if author.get("id") is not None else None,
        body=str(message.get("content") or ""),
        created_at=created_at,
        reply_to_message_id=(
            str(message["message_reference"]["message_id"])
            if (message.get("message_reference") or {}).get("message_id") is not None
            else None
        ),
        thread_id=(
            str(thread_id)
            if thread_id
            else (str(guild_id) if message.get("type") == 11 else None)
        ),
        edited_at=_parse_timestamp(message.get("edited_timestamp")),
        source_url=None,
        is_bot=bool(author.get("bot", False)),
    )
