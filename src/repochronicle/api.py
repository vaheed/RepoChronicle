"""HTTP API for health, configuration status, and future project operations."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException

from repochronicle import __version__
from repochronicle.config import get_settings

logger = logging.getLogger("repochronicle.api")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logging.basicConfig(level=get_settings().log_level.upper())
    yield


app = FastAPI(
    title="RepoChronicle API",
    description="Open-source project intelligence for code, Git activity, and team conversations.",
    version=__version__,
    lifespan=lifespan,
)


@app.get("/health/live", tags=["health"])
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", tags=["health"])
async def readiness() -> dict[str, str]:
    # Keep liveness/status importable before optional infrastructure is reachable.
    import asyncpg
    from redis.asyncio import Redis

    settings = get_settings()
    try:
        conn = await asyncpg.connect(
            settings.database_url,
            timeout=settings.database_connect_timeout_seconds,
        )
        try:
            await conn.fetchval("SELECT 1")
        finally:
            await conn.close()
    except Exception as exc:
        logger.warning("readiness_database_failed", extra={"error_type": type(exc).__name__})
        raise HTTPException(status_code=503, detail="database_not_ready") from exc

    try:
        client: Redis = Redis.from_url(settings.valkey_url, socket_connect_timeout=2)
        try:
            await client.ping()
        finally:
            await client.aclose()
    except Exception as exc:
        logger.warning("readiness_valkey_failed", extra={"error_type": type(exc).__name__})
        raise HTTPException(status_code=503, detail="valkey_not_ready") from exc

    return {"status": "ready", "database": "ok", "queue": "ok"}


@app.get("/v1/status", tags=["status"])
async def service_status() -> dict[str, object]:
    settings = get_settings()
    return {
        "name": "RepoChronicle",
        "version": __version__,
        "phase": "F0",
        "project_status": "foundation_scaffold",
        "features": {
            "api_health": "implemented",
            "database_schema": "implemented",
            "bootstrap_state_machine": "implemented_contract_only",
            "initial_repository_full_scan": "planned_F1",
            "incremental_git_sync": "planned_F1_F2",
            "code_retrieval": "planned_F3",
            "local_embedding_adapter": "implemented_adapter_optional_extra",
            "openai_compatible_chat_adapter": "implemented_adapter",
            "mcp_project_status": "implemented",
            "telegram_ingestion": "planned_F5",
            "discord_ingestion": "planned_F5",
            "fine_tuning": "planned_optional_F6",
        },
        "configuration": {
            "embedding_enabled": settings.embedding_enabled,
            "embedding_provider": settings.embedding_provider,
            "llm_configured": bool(settings.llm_base_url and settings.llm_model),
        },
        "note": "This foundation scaffold does not yet perform end-to-end repository ingestion.",
    }
