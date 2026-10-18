"""Minimal versioned SQL migration runner for PostgreSQL."""

import asyncio
import logging
from pathlib import Path

import asyncpg

from repochronicle.config import get_settings

PACKAGE_MIGRATIONS_DIR = Path(__file__).resolve().parent / "sql"
SOURCE_MIGRATIONS_DIR = Path(__file__).resolve().parents[3] / "migrations"
MIGRATIONS_DIR = (
    PACKAGE_MIGRATIONS_DIR if PACKAGE_MIGRATIONS_DIR.is_dir() else SOURCE_MIGRATIONS_DIR
)


async def upgrade() -> None:
    settings = get_settings()
    connection = await asyncpg.connect(
        settings.database_url,
        timeout=settings.database_connect_timeout_seconds,
    )
    try:
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        for path in sorted(MIGRATIONS_DIR.glob("[0-9][0-9][0-9]_*.sql")):
            already_applied = await connection.fetchval(
                "SELECT EXISTS(SELECT 1 FROM schema_migrations WHERE version = $1)",
                path.name,
            )
            if already_applied:
                continue
            sql = path.read_text(encoding="utf-8")
            async with connection.transaction():
                await connection.execute(sql)
                await connection.execute(
                    "INSERT INTO schema_migrations(version) VALUES($1)",
                    path.name,
                )
            logging.info("migration_applied", extra={"version": path.name})
    finally:
        await connection.close()


def main() -> None:
    logging.basicConfig(level=get_settings().log_level.upper())
    asyncio.run(upgrade())


if __name__ == "__main__":
    main()
