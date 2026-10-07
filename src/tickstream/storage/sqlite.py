"""SQLite-backed trade repository."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import aiosqlite
import structlog

from tickstream.schemas import Exchange, Side, Trade
from tickstream.storage.base import TradeRepository

logger = structlog.get_logger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS trades (
    exchange TEXT NOT NULL,
    symbol TEXT NOT NULL,
    trade_id INTEGER NOT NULL,
    price TEXT NOT NULL,
    quantity TEXT NOT NULL,
    side TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    ingested_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    PRIMARY KEY (exchange, symbol, trade_id)
);
CREATE INDEX IF NOT EXISTS idx_trades_symbol_timestamp
    ON trades (symbol, timestamp DESC);
"""


class SQLiteTradeRepository(TradeRepository):
    """Persist trades in a local SQLite database.

    Decimal values are stored as TEXT to preserve exact precision.
    The composite primary key (exchange, symbol, trade_id) prevents
    duplicate inserts via ``INSERT OR IGNORE``.
    """

    def __init__(self, db_path: str | Path = "tickstream.db") -> None:
        self._db_path = str(db_path)
        self._conn: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        if self._conn is not None:
            return
        self._conn = await aiosqlite.connect(self._db_path)
        await self._conn.executescript(_SCHEMA)
        await self._conn.commit()
        logger.info("sqlite.initialized", path=self._db_path)

    async def save_trades(self, trades: Sequence[Trade]) -> int:
        if self._conn is None:
            msg = "initialize() must be called before save_trades()"
            raise RuntimeError(msg)
        if not trades:
            return 0
        rows = [
            (
                t.exchange.value,
                t.symbol,
                t.trade_id,
                str(t.price),
                str(t.quantity),
                t.side.value,
                t.timestamp.isoformat(),
            )
            for t in trades
        ]
        cursor = await self._conn.executemany(
            "INSERT OR IGNORE INTO trades "
            "(exchange, symbol, trade_id, price, quantity, side, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        inserted = cursor.rowcount if cursor.rowcount is not None else 0
        await self._conn.commit()
        return inserted

    async def count_trades(self) -> int:
        if self._conn is None:
            msg = "initialize() must be called before count_trades()"
            raise RuntimeError(msg)
        async with self._conn.execute("SELECT COUNT(*) FROM trades") as cursor:
            row = await cursor.fetchone()
            return int(row[0]) if row else 0

    async def fetch_recent(self, limit: int = 10) -> list[Trade]:
        if self._conn is None:
            msg = "initialize() must be called before fetch_recent()"
            raise RuntimeError(msg)
        if limit <= 0:
            return []
        cursor = await self._conn.execute(
            "SELECT exchange, symbol, trade_id, price, quantity, side, timestamp "
            "FROM trades ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [_row_to_trade(row) for row in rows]

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None
            logger.info("sqlite.closed", path=self._db_path)


def _row_to_trade(row: Sequence[object]) -> Trade:
    exchange, symbol, trade_id, price, quantity, side, timestamp = row
    return Trade(
        exchange=Exchange(str(exchange)),
        symbol=str(symbol),
        trade_id=int(str(trade_id)),
        price=Decimal(str(price)),
        quantity=Decimal(str(quantity)),
        side=Side(str(side)),
        timestamp=datetime.fromisoformat(str(timestamp)),
    )
