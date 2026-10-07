"""Tests for SQLiteTradeRepository."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from tickstream.schemas import Exchange, Side, Trade
from tickstream.storage.sqlite import SQLiteTradeRepository


def _trade(trade_id: int, symbol: str = "BTCUSDT", offset_s: int = 0) -> Trade:
    return Trade(
        exchange=Exchange.BINANCE,
        symbol=symbol,
        trade_id=trade_id,
        price=Decimal("50000.00"),
        quantity=Decimal("0.001"),
        side=Side.BUY,
        timestamp=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(seconds=offset_s),
    )


async def _make_repo(tmp_path: Path) -> SQLiteTradeRepository:
    repo = SQLiteTradeRepository(tmp_path / "test.db")
    await repo.initialize()
    return repo


@pytest.mark.asyncio
async def test_initialize_creates_table(tmp_path: Path) -> None:
    repo = await _make_repo(tmp_path)
    try:
        assert await repo.count_trades() == 0
    finally:
        await repo.close()


@pytest.mark.asyncio
async def test_save_trades_inserts_rows(tmp_path: Path) -> None:
    repo = await _make_repo(tmp_path)
    try:
        inserted = await repo.save_trades([_trade(1), _trade(2), _trade(3)])
        assert inserted == 3
        assert await repo.count_trades() == 3
    finally:
        await repo.close()


@pytest.mark.asyncio
async def test_save_trades_is_idempotent(tmp_path: Path) -> None:
    repo = await _make_repo(tmp_path)
    try:
        first = await repo.save_trades([_trade(1), _trade(2)])
        second = await repo.save_trades([_trade(1), _trade(2)])
        assert first == 2
        assert second == 0
        assert await repo.count_trades() == 2
    finally:
        await repo.close()


@pytest.mark.asyncio
async def test_save_empty_returns_zero(tmp_path: Path) -> None:
    repo = await _make_repo(tmp_path)
    try:
        assert await repo.save_trades([]) == 0
    finally:
        await repo.close()


@pytest.mark.asyncio
async def test_fetch_recent_orders_by_timestamp_desc(tmp_path: Path) -> None:
    repo = await _make_repo(tmp_path)
    try:
        await repo.save_trades(
            [
                _trade(1, offset_s=0),
                _trade(2, offset_s=10),
                _trade(3, offset_s=5),
            ]
        )
        recent = await repo.fetch_recent(limit=2)
        assert [t.trade_id for t in recent] == [2, 3]
    finally:
        await repo.close()


@pytest.mark.asyncio
async def test_fetch_recent_preserves_decimal_precision(tmp_path: Path) -> None:
    repo = await _make_repo(tmp_path)
    try:
        await repo.save_trades([_trade(1)])
        [restored] = await repo.fetch_recent(limit=1)
        assert restored.price == Decimal("50000.00")
        assert restored.quantity == Decimal("0.001")
    finally:
        await repo.close()


@pytest.mark.asyncio
async def test_fetch_recent_limit_zero_returns_empty(tmp_path: Path) -> None:
    repo = await _make_repo(tmp_path)
    try:
        await repo.save_trades([_trade(1)])
        assert await repo.fetch_recent(limit=0) == []
    finally:
        await repo.close()


@pytest.mark.asyncio
async def test_save_before_initialize_raises(tmp_path: Path) -> None:
    repo = SQLiteTradeRepository(tmp_path / "uninitialized.db")
    with pytest.raises(RuntimeError, match="initialize"):
        await repo.save_trades([_trade(1)])


@pytest.mark.asyncio
async def test_count_before_initialize_raises(tmp_path: Path) -> None:
    repo = SQLiteTradeRepository(tmp_path / "uninitialized.db")
    with pytest.raises(RuntimeError, match="initialize"):
        await repo.count_trades()
