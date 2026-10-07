"""Tests for tickstream.schemas."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from tickstream.schemas import Exchange, OrderBookLevel, Side, Trade


def _valid_trade_kwargs() -> dict[str, object]:
    return {
        "exchange": Exchange.BINANCE,
        "symbol": "BTCUSDT",
        "trade_id": 12345,
        "price": Decimal("50000.00"),
        "quantity": Decimal("0.001"),
        "side": Side.BUY,
        "timestamp": datetime(2026, 1, 1, tzinfo=UTC),
    }


def test_trade_valid() -> None:
    trade = Trade(**_valid_trade_kwargs())  # type: ignore[arg-type]
    assert trade.price == Decimal("50000.00")
    assert trade.side is Side.BUY
    assert trade.exchange is Exchange.BINANCE


def test_trade_rejects_negative_price() -> None:
    kwargs = _valid_trade_kwargs()
    kwargs["price"] = Decimal("-1")
    with pytest.raises(ValidationError):
        Trade(**kwargs)  # type: ignore[arg-type]


def test_trade_rejects_zero_quantity() -> None:
    kwargs = _valid_trade_kwargs()
    kwargs["quantity"] = Decimal("0")
    with pytest.raises(ValidationError):
        Trade(**kwargs)  # type: ignore[arg-type]


def test_trade_is_immutable() -> None:
    trade = Trade(**_valid_trade_kwargs())  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        trade.price = Decimal("60000")  # type: ignore[misc]


def test_order_book_level_allows_zero_quantity() -> None:
    level = OrderBookLevel(price=Decimal("50000"), quantity=Decimal("0"))
    assert level.quantity == Decimal("0")


def test_order_book_level_rejects_negative_price() -> None:
    with pytest.raises(ValidationError):
        OrderBookLevel(price=Decimal("-1"), quantity=Decimal("1"))
