"""Live demo: connect to Binance and print the first N trades.

Usage:

    python scripts/live_demo.py

Optional environment variables:

    TICKSTREAM_DEMO_SYMBOLS    Comma-separated symbols (default: btcusdt)
    TICKSTREAM_DEMO_COUNT      Number of trades to print (default: 5)
"""

from __future__ import annotations

import asyncio
import os
import sys
from contextlib import aclosing

from tickstream.config import LogLevel, get_settings
from tickstream.exchanges.binance import BinanceClient


async def main() -> int:
    settings = get_settings()
    symbols_env = os.getenv("TICKSTREAM_DEMO_SYMBOLS", "btcusdt")
    symbols = [s.strip().lower() for s in symbols_env.split(",") if s.strip()]
    count = int(os.getenv("TICKSTREAM_DEMO_COUNT", "5"))

    print(f"Connecting to Binance for symbols: {symbols}")
    print(f"Will print the first {count} trades, then exit.\n")

    client = BinanceClient()
    printed = 0

    try:
        async with aclosing(client.stream_trades(symbols)) as stream:
            async for trade in stream:
                print(
                    f"[{trade.timestamp.isoformat()}] "
                    f"{trade.symbol:<10} "
                    f"{trade.side.value:<4} "
                    f"price={trade.price} "
                    f"qty={trade.quantity} "
                    f"id={trade.trade_id}"
                )
                printed += 1
                if printed >= count:
                    client.stop()
                    break
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130

    print(f"\nDone. Printed {printed} trades.")
    print(
        f"Environment: {settings.environment.value}, "
        f"log level: {settings.log_level.value}"
    )
    if settings.log_level is LogLevel.DEBUG:
        print("(DEBUG mode enabled)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
