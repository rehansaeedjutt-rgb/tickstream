"""Live demo: connect to Binance, persist trades, then print a summary.

Usage:

    python scripts/live_demo.py

Optional environment variables:

    TICKSTREAM_DEMO_SYMBOLS    Comma-separated symbols (default: btcusdt)
    TICKSTREAM_DEMO_COUNT      Number of trades to capture (default: 5)
    TICKSTREAM_DEMO_DB         SQLite database path (default: tickstream.db)
"""

from __future__ import annotations

import asyncio
import os
import sys
from contextlib import aclosing

from tickstream.config import LogLevel, get_settings
from tickstream.exchanges.binance import BinanceClient
from tickstream.storage.sqlite import SQLiteTradeRepository


async def main() -> int:
    settings = get_settings()
    symbols_env = os.getenv("TICKSTREAM_DEMO_SYMBOLS", "btcusdt")
    symbols = [s.strip().lower() for s in symbols_env.split(",") if s.strip()]
    count = int(os.getenv("TICKSTREAM_DEMO_COUNT", "5"))
    db_path = os.getenv("TICKSTREAM_DEMO_DB", "tickstream.db")

    print(f"Symbols: {symbols}")
    print(f"Capture count: {count}")
    print(f"Database: {db_path}\n")

    repo = SQLiteTradeRepository(db_path)
    await repo.initialize()

    client = BinanceClient()
    captured = 0

    try:
        async with aclosing(client.stream_trades(symbols)) as stream:
            async for trade in stream:
                inserted = await repo.save_trades([trade])
                status = "stored" if inserted else "duplicate"
                print(
                    f"[{trade.timestamp.isoformat()}] "
                    f"{trade.symbol:<10} "
                    f"{trade.side.value:<4} "
                    f"price={trade.price} "
                    f"qty={trade.quantity} "
                    f"id={trade.trade_id} "
                    f"({status})"
                )
                captured += 1
                if captured >= count:
                    client.stop()
                    break
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        await repo.close()
        return 130

    total = await repo.count_trades()
    recent = await repo.fetch_recent(limit=3)

    print(f"\nCaptured {captured} trades.")
    print(f"Total trades in DB: {total}")
    print("\nMost recent 3 trades from DB:")
    for t in recent:
        print(f"  {t.timestamp.isoformat()}  {t.symbol}  {t.side.value}  {t.price} x {t.quantity}")

    await repo.close()
    print(f"\nEnvironment: {settings.environment.value}, log level: {settings.log_level.value}")
    if settings.log_level is LogLevel.DEBUG:
        print("(DEBUG mode enabled)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
