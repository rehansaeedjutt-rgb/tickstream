"""Binance WebSocket client."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import structlog
import websockets
from websockets.exceptions import ConnectionClosed

from tickstream.config import get_settings
from tickstream.exchanges.base import ExchangeClient
from tickstream.schemas import Exchange, Side, Trade

logger = structlog.get_logger(__name__)


class BinanceClient(ExchangeClient):
    """Streams trade events from Binance's public WebSocket API.

    Uses the combined-stream endpoint:
    ``wss://stream.binance.com:9443/stream?streams=btcusdt@trade/ethusdt@trade``

    No API key is required for public market data.
    """

    def __init__(self, ws_base_url: str | None = None) -> None:
        settings = get_settings()
        self._ws_base_url = ws_base_url or settings.binance_ws_base_url
        self._reconnect_base = settings.reconnect_base_delay_seconds
        self._reconnect_max = settings.reconnect_max_delay_seconds
        self._stopped = False

    @property
    def name(self) -> str:
        return "binance"

    def stop(self) -> None:
        """Signal the client to stop after the current message."""
        self._stopped = True

    async def stream_trades(self, symbols: list[str]) -> AsyncIterator[Trade]:
        """Stream trades for the given symbols with automatic reconnection."""
        if not symbols:
            msg = "symbols must be a non-empty list"
            raise ValueError(msg)

        normalized = [s.lower() for s in symbols]
        url = self._build_stream_url(normalized)
        attempt = 0

        while not self._stopped:
            try:
                logger.info("binance.connecting", url=url)
                async with websockets.connect(
                    url, ping_interval=20, ping_timeout=20
                ) as ws:
                    logger.info("binance.connected")
                    attempt = 0
                    async for raw in ws:
                        if self._stopped:
                            return
                        trade = self._parse_message(raw)
                        if trade is not None:
                            yield trade
                            if self._stopped:
                                return
            except (TimeoutError, ConnectionClosed, OSError) as exc:
                attempt += 1
                delay = min(
                    self._reconnect_base * (2 ** (attempt - 1)),
                    self._reconnect_max,
                )
                logger.warning(
                    "binance.connection_lost",
                    attempt=attempt,
                    delay_seconds=delay,
                    error=str(exc),
                )
                await asyncio.sleep(delay)

    def _build_stream_url(self, symbols: list[str]) -> str:
        streams = "/".join(f"{s}@trade" for s in symbols)
        base = self._ws_base_url.rstrip("/")
        if base.endswith("/ws"):
            base = base[:-3]
        return f"{base}/stream?streams={streams}"

    def _parse_message(self, raw: str | bytes) -> Trade | None:
        """Parse a combined-stream message and return a Trade, or None on skip."""
        try:
            payload: dict[str, Any] = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            logger.warning(
                "binance.invalid_json",
                raw=raw[:200] if isinstance(raw, str) else "<bytes>",
            )
            return None

        data = payload.get("data")
        if not isinstance(data, dict):
            return None

        try:
            is_buyer_maker = bool(data["m"])
            return Trade(
                exchange=Exchange.BINANCE,
                symbol=str(data["s"]),
                trade_id=int(data["t"]),
                price=Decimal(str(data["p"])),
                quantity=Decimal(str(data["q"])),
                side=Side.SELL if is_buyer_maker else Side.BUY,
                timestamp=datetime.fromtimestamp(int(data["T"]) / 1000, tz=UTC),
            )
        except (KeyError, ValueError, ArithmeticError) as exc:
            logger.warning("binance.parse_failed", error=str(exc), data=data)
            return None
