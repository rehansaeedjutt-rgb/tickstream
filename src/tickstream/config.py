"""Application configuration loaded from environment variables."""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Deployment environment."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(StrEnum):
    """Structured logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Runtime settings for tickstream.

    All values can be overridden via environment variables prefixed with
    ``TICKSTREAM_`` (e.g. ``TICKSTREAM_LOG_LEVEL=DEBUG``) or via a local
    ``.env`` file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="TICKSTREAM_",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Environment = Environment.DEVELOPMENT
    log_level: LogLevel = LogLevel.INFO
    log_json: bool = False

    binance_ws_base_url: str = "wss://stream.binance.com:9443/ws"
    binance_rest_base_url: str = "https://api.binance.com"

    symbols: list[str] = Field(default_factory=lambda: ["btcusdt", "ethusdt"])
    reconnect_base_delay_seconds: float = 1.0
    reconnect_max_delay_seconds: float = 60.0


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
