from datetime import UTC, datetime

from repochronicle.connectors.discord import normalize_discord_message
from repochronicle.connectors.telegram import normalize_telegram_update


def test_telegram_group_message_normalizes_stable_ids_and_reply() -> None:
    result = normalize_telegram_update(
        {
            "update_id": 100,
            "message": {
                "message_id": 45,
                "date": 1_750_000_000,
                "text": "Where is auth?",
                "chat": {"id": -100200300, "type": "supergroup"},
                "from": {"id": 77, "is_bot": False},
                "reply_to_message": {"message_id": 44},
                "message_thread_id": 12,
            },
        },
        source_id="telegram-group-1",
    )

    assert result is not None
    assert result.platform == "telegram"
    assert result.external_message_id == "45"
    assert result.external_channel_id == "-100200300"
    assert result.reply_to_message_id == "44"
    assert result.thread_id == "12"
    assert result.created_at.tzinfo == UTC


def test_telegram_service_update_without_message_is_ignored() -> None:
    assert normalize_telegram_update({"update_id": 2}, source_id="src") is None


def test_discord_message_normalizes_edited_timestamp_and_thread() -> None:
    result = normalize_discord_message(
        {
            "id": "123456789",
            "channel_id": "444",
            "guild_id": "333",
            "timestamp": "2026-10-18T12:00:00.000Z",
            "edited_timestamp": "2026-10-18T12:05:00.000Z",
            "content": "Latest message",
            "author": {"id": "22", "bot": False},
            "thread_id": "777",
            "message_reference": {"message_id": "111"},
        },
        source_id="discord-channel-1",
    )

    assert result is not None
    assert result.external_channel_id == "444"
    assert result.thread_id == "777"
    assert result.reply_to_message_id == "111"
    assert result.edited_at == datetime(2026, 10, 18, 12, 5, tzinfo=UTC)


def test_discord_payload_without_required_fields_is_ignored() -> None:
    assert normalize_discord_message({}, source_id="src") is None


def test_discord_message_with_naive_timestamp_is_ignored() -> None:
    assert (
        normalize_discord_message(
            {"id": "1", "channel_id": "2", "timestamp": "2026-10-18T12:00:00"},
            source_id="src",
        )
        is None
    )


def test_telegram_message_with_invalid_timestamp_is_ignored() -> None:
    assert (
        normalize_telegram_update(
            {
                "message": {
                    "message_id": 1,
                    "date": "not-a-timestamp",
                    "chat": {"id": 2},
                }
            },
            source_id="src",
        )
        is None
    )
