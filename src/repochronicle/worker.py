"""Long-running worker process scaffold.

The queue consumer and durable job executor are implemented in later roadmap phases.
This process currently verifies connectivity and stays ready without consuming or
acknowledging feature jobs that have not been implemented.
"""

import asyncio
import logging
from contextlib import suppress

import asyncpg
from redis.asyncio import Redis

from repochronicle.config import get_settings

logger = logging.getLogger("repochronicle.worker")


async def run() -> None:
    logging.basicConfig(level=get_settings().log_level.upper())
    settings = get_settings()
    logger.info("worker_starting", extra={"phase": "F0"})
    while True:
        try:
            conn = await asyncpg.connect(
                settings.database_url,
                timeout=settings.database_connect_timeout_seconds,
            )
            try:
                await conn.execute("SELECT 1")
            finally:
                await conn.close()
            client = Redis.from_url(settings.valkey_url, socket_connect_timeout=2)
            try:
                await client.ping()
            finally:
                await client.aclose()
            logger.debug("worker_dependencies_ready")
        except Exception as exc:
            logger.warning(
                "worker_dependency_check_failed",
                extra={"error_type": type(exc).__name__},
            )
        await asyncio.sleep(30)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(run())
