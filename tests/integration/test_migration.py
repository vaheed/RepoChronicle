"""Integration smoke test. CI runs this only after applying migrations to pgvector."""

import os

import pytest

asyncpg = pytest.importorskip("asyncpg")


@pytest.mark.asyncio
async def test_foundation_schema_is_available_when_database_is_configured() -> None:
    database_url = os.environ.get("RC_DATABASE_URL")
    if not database_url:
        pytest.skip(
            "RC_DATABASE_URL is not set; integration database is only available in CI/Compose"
        )
    connection = await asyncpg.connect(database_url)
    try:
        assert await connection.fetchval("SELECT count(*) FROM schema_migrations") >= 1
        assert await connection.fetchval(
            "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
        )
        assert await connection.fetchval(
            "SELECT to_regclass('public.embedding_spaces') IS NOT NULL"
        )
    finally:
        await connection.close()
