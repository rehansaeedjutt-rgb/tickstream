"""Command-line entry point for tickstream."""

from __future__ import annotations

import argparse
import asyncio
import sys
from contextlib import aclosing

import structlog

from tickstream import __version__
from tickstream.config import get_settings
from tickstream.exchanges.binance import BinanceClient
from tickstream.storage.sqlite import SQLiteTradeRepository

logger = structlog.get_logger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tickstream",
        description="Real-time crypto market data ingestion.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"tickstream {__version__}",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="Capture a few live trades and persist them.")
    demo.add_argument(
        "--symbols",
        default=",".join(get_settings().symbols),
        help="Comma-separated lowercase symbols (default: from settings).",
    )
    demo.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of trades to capture before exiting (default: 5).",
    )
    demo.add_argument(
        "--db",
        default="tickstream.db",
        help="SQLite database path (default: tickstream.db).",
    )

    return parser


async def _run_demo(symbols: list[str], count: int, db_path: str) -> int:
    if count <= 0:
        print("count must be positive", file=sys.stderr)
        return 2

    repo = SQLiteTradeRepository(db_path)
    await repo.initialize()
    client = BinanceClient()
    captured = 0

    try:
        async with aclosing(client.stream_trades(symbols)) as stream:
            async for trade in stream:
                inserted = await repo.save_trades([trade])
                marker = "stored" if inserted else "duplicate"
                print(
                    f"[{trade.timestamp.isoformat()}] "
                    f"{trade.symbol:<10} {trade.side.value:<4} "
                    f"price={trade.price} qty={trade.quantity} "
                    f"id={trade.trade_id} ({marker})"
                )
                captured += 1
                if captured >= count:
                    client.stop()
                    break
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        await repo.close()
        return 130

    total = await repo.count_trades()
    print(f"\nCaptured {captured} trades. Total in DB: {total}")
    await repo.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "demo":
        symbols = [s.strip().lower() for s in args.symbols.split(",") if s.strip()]
        return asyncio.run(_run_demo(symbols, args.count, args.db))

    parser.error(f"unknown command: {args.command}")
    return 2  # unreachable, but mypy-friendly


if __name__ == "__main__":
    sys.exit(main())
