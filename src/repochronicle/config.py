"""Environment-backed configuration for RepoChronicle."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RC_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = "development"
    log_level: str = "INFO"
    public_api_url: str = "http://localhost:8080"
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8090

    database_url: str = (
        "postgresql://repochronicle:change-me-local-only@localhost:5432/"
        "repochronicle"
    )
    valkey_url: str = "redis://localhost:6379/0"
    database_connect_timeout_seconds: float = Field(default=5.0, gt=0, le=60)
    provider_http_timeout_seconds: float = Field(default=30.0, gt=0, le=300)
    max_context_chars: int = Field(default=24000, ge=1000, le=1_000_000)

    llm_provider: str = "openai-compatible"
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""

    embedding_provider: str = "local"
    embedding_base_url: str = ""
    embedding_api_key: str = ""
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimensions: int = Field(default=384, ge=1, le=16000)
    embedding_enabled: bool = True

    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""
    telegram_allowed_chat_ids: str = ""
    telegram_default_mode: str = "mention_only"

    discord_bot_token: str = ""
    discord_allowed_guild_ids: str = ""
    discord_allowed_channel_ids: str = ""
    discord_default_mode: str = "mention_only"

    allowed_git_hosts: str = "github.com,gitlab.com"
    bootstrap_max_file_bytes: int = Field(default=2_000_000, ge=1024)
    bootstrap_max_repository_bytes: int = Field(default=2_000_000_000, ge=1_000_000)
    bootstrap_backfill_days: int = Field(default=365, ge=0, le=36500)
    reconciliation_interval_seconds: int = Field(default=21600, ge=60)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
