"""Telegram Bot API event normalization (no network polling in the F0 scaffold)."""

from datetime import UTC, datetime
from typing import Any

from repochronicle.connectors.events import NormalizedMessage


def normalize_telegram_update(
    update: dict[str, Any], *, source_id: str
) -> NormalizedMessage | None:
    message = (
        update.get("message")
        or update.get("edited_message")
        or update.get("channel_post")
        or update.get("edited_channel_post")
    )
    if not isinstance(message, dict):
        return None
    chat = message.get("chat") or {}
    sender = message.get("from") or {}
    message_id = message.get("message_id")
    chat_id = chat.get("id")
    sent_at = message.get("date")
    if message_id is None or chat_id is None or sent_at is None:
        return None
    body = message.get("text") or message.get("caption") or ""
    reply = message.get("reply_to_message") or {}
    try:
        if isinstance(sent_at, datetime):
            if sent_at.tzinfo is None:
                return None
            created_at = sent_at.astimezone(UTC)
        else:
            created_at = datetime.fromtimestamp(int(sent_at), tz=UTC)
    except (OverflowError, OSError, TypeError, ValueError):
        return None
    edit_timestamp = message.get("edit_date")
    try:
        edited_at = (
            datetime.fromtimestamp(int(edit_timestamp), tz=UTC)
            if edit_timestamp is not None
            else None
        )
    except (OverflowError, OSError, TypeError, ValueError):
        edited_at = None
    sender_id = sender.get("id")
    return NormalizedMessage(
        platform="telegram",
        source_id=source_id,
        external_message_id=str(message_id),
        external_channel_id=str(chat_id),
        external_author_id=str(sender_id) if sender_id is not None else None,
        body=str(body),
        created_at=created_at,
        reply_to_message_id=(
            str(reply["message_id"]) if reply.get("message_id") is not None else None
        ),
        thread_id=str(message["message_thread_id"]) if message.get("message_thread_id") else None,
        edited_at=edited_at,
        is_bot=bool(sender.get("is_bot", False)),
    )
