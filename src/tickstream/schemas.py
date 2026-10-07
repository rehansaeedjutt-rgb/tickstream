"""Pydantic models for validated market-data messages."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Exchange(StrEnum):
    """Supported exchanges."""

    BINANCE = "binance"
    OKX = "okx"
    BYBIT = "bybit"


class Side(StrEnum):
    """Trade aggressor side."""

    BUY = "BUY"
    SELL = "SELL"


class Trade(BaseModel):
    """A single executed trade from an exchange."""

    model_config = ConfigDict(frozen=True)

    exchange: Exchange
    symbol: str
    trade_id: int
    price: Decimal = Field(..., gt=0)
    quantity: Decimal = Field(..., gt=0)
    side: Side
    timestamp: datetime


class OrderBookLevel(BaseModel):
    """A single price level in an order book."""

    model_config = ConfigDict(frozen=True)

    price: Decimal = Field(..., gt=0)
    quantity: Decimal = Field(..., ge=0)


class OrderBookSnapshot(BaseModel):
    """A snapshot of the top-N order book levels."""

    model_config = ConfigDict(frozen=True)

    exchange: Exchange
    symbol: str
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]
    timestamp: datetime
