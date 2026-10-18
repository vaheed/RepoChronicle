"""Long-running chat connector service scaffold."""

import asyncio
import logging
from contextlib import suppress

from repochronicle.config import get_settings

logger = logging.getLogger("repochronicle.connectors")


async def run() -> None:
    logging.basicConfig(level=get_settings().log_level.upper())
    settings = get_settings()
    configured = {
        "telegram": bool(settings.telegram_bot_token),
        "discord": bool(settings.discord_bot_token),
    }
    logger.info(
        "connector_runtime_started",
        extra={
            "phase": "F0",
            "telegram_configured": configured["telegram"],
            "discord_configured": configured["discord"],
            "note": (
                "Platform event ingestion is planned for F5; "
                "credentials are not used by this scaffold."
            ),
        },
    )
    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(run())
