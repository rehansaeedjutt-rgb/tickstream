"""Unit tests for the Binance client — no network calls."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from tickstream.exchanges.binance import BinanceClient
from tickstream.schemas import Exchange, Side


def _client() -> BinanceClient:
    return BinanceClient(ws_base_url="wss://stream.binance.com:9443/ws")


def _valid_trade_payload() -> dict[str, object]:
    return {
        "stream": "btcusdt@trade",
        "data": {
            "e": "trade",
            "E": 1700000000000,
            "s": "BTCUSDT",
            "t": 12345,
            "p": "50000.00",
            "q": "0.001",
            "T": 1700000000000,
            "m": False,
        },
    }


def test_client_name() -> None:
    assert _client().name == "binance"


def test_stop_sets_flag() -> None:
    client = _client()
    assert client._stopped is False
    client.stop()
    assert client._stopped is True


def test_build_stream_url_single_symbol() -> None:
    url = _client()._build_stream_url(["btcusdt"])
    assert url == "wss://stream.binance.com:9443/stream?streams=btcusdt@trade"


def test_build_stream_url_multiple_symbols() -> None:
    url = _client()._build_stream_url(["btcusdt", "ethusdt"])
    assert url == ("wss://stream.binance.com:9443/stream?streams=btcusdt@trade/ethusdt@trade")


def test_parse_message_valid_trade() -> None:
    raw = json.dumps(_valid_trade_payload())
    trade = _client()._parse_message(raw)
    assert trade is not None
    assert trade.exchange is Exchange.BINANCE
    assert trade.symbol == "BTCUSDT"
    assert trade.trade_id == 12345
    assert trade.price == Decimal("50000.00")
    assert trade.quantity == Decimal("0.001")
    assert trade.side is Side.BUY
    assert trade.timestamp == datetime.fromtimestamp(1700000000, tz=UTC)


def test_parse_message_buyer_is_maker_maps_to_sell() -> None:
    payload = _valid_trade_payload()
    data = payload["data"]
    assert isinstance(data, dict)
    data["m"] = True
    trade = _client()._parse_message(json.dumps(payload))
    assert trade is not None
    assert trade.side is Side.SELL


def test_parse_message_invalid_json_returns_none() -> None:
    assert _client()._parse_message("not-json{") is None


def test_parse_message_missing_data_returns_none() -> None:
    assert _client()._parse_message(json.dumps({"stream": "btcusdt@trade"})) is None


def test_parse_message_missing_required_field_returns_none() -> None:
    payload = _valid_trade_payload()
    data = payload["data"]
    assert isinstance(data, dict)
    del data["p"]  # remove price
    assert _client()._parse_message(json.dumps(payload)) is None


def test_parse_message_non_numeric_price_returns_none() -> None:
    payload = _valid_trade_payload()
    data = payload["data"]
    assert isinstance(data, dict)
    data["p"] = "not-a-number"
    assert _client()._parse_message(json.dumps(payload)) is None


@pytest.mark.asyncio
async def test_stream_trades_rejects_empty_symbols() -> None:
    client = _client()
    with pytest.raises(ValueError, match="non-empty"):
        async for _ in client.stream_trades([]):
            pass
