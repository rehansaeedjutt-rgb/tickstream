"""Tests for tickstream.config."""

from tickstream.config import Environment, LogLevel, Settings


def test_settings_defaults() -> None:
    settings = Settings()
    assert settings.environment is Environment.DEVELOPMENT
    assert settings.log_level is LogLevel.INFO
    assert settings.log_json is False


def test_settings_default_symbols() -> None:
    settings = Settings()
    assert "btcusdt" in settings.symbols
    assert "ethusdt" in settings.symbols


def test_settings_accepts_exchange_endpoints() -> None:
    settings = Settings()
    assert settings.binance_ws_base_url.startswith("wss://")
    assert settings.binance_rest_base_url.startswith("https://")


def test_settings_reconnect_bounds() -> None:
    settings = Settings()
    assert settings.reconnect_base_delay_seconds > 0
    assert settings.reconnect_max_delay_seconds >= settings.reconnect_base_delay_seconds
