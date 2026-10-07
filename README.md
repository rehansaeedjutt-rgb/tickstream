# tickstream

> A production-grade, real-time crypto market data engine.

[![CI](https://github.com/rehansaeedjutt-rgb/tickstream/actions/workflows/ci.yml/badge.svg)](https://github.com/rehansaeedjutt-rgb/tickstream/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Coverage](https://img.shields.io/badge/coverage-83%25-brightgreen.svg)](#testing)

## Overview

`tickstream` ingests real-time market data from major crypto exchanges via WebSocket,
validates every message at the boundary, and persists it for downstream research,
analytics, and risk systems.

**Current status:** Phase 1 complete — Binance WebSocket ingestion + SQLite persistence.

## Why this project exists

Most retail crypto tooling is either a one-off script with no error handling, or a
black box. `tickstream` is built the way an exchange or quant desk would build it:
async-first, exchange-agnostic, validated at the boundary, and observable in production.

## Architecture

    Exchange WS  -->  Normalizer  -->  Validator  -->  Repository  -->  SQLite
                           |                              |
                           +--->  Structured Logs  <------+
                           |
                           +--->  Reconnect (exp backoff)

Key design choices:

- **Async-first**: `asyncio` + `websockets` for non-blocking ingestion.
- **Validated at the boundary**: every message parsed into a pydantic `Trade` model.
- **Idempotent storage**: `(exchange, symbol, trade_id)` primary key — replays are safe.
- **Exact precision**: prices and quantities stored as `Decimal` (TEXT in SQLite).
- **Resilient**: automatic reconnect with exponential backoff (1s → 60s cap).
- **Observable**: structured logs via `structlog`.

## Live demo

Clone, install, and run against Binance's public WebSocket — no API key required:

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python scripts/live_demo.py
```

Example output (real trades, real timestamps):

```
Symbols: ['btcusdt']
Capture count: 5
Database: tickstream.db

[2026-10-07T05:17:13.137000+00:00] BTCUSDT    SELL price=84170.00000000 qty=0.00079000 id=6741801199 (stored)
[2026-10-07T05:17:13.507000+00:00] BTCUSDT    BUY  price=84170.01000000 qty=0.00116000 id=6741801200 (stored)
[2026-10-07T05:17:13.725000+00:00] BTCUSDT    SELL price=84170.00000000 qty=0.00246000 id=6741801201 (stored)
[2026-10-07T05:17:13.803000+00:00] BTCUSDT    BUY  price=84170.01000000 qty=0.01239000 id=6741801202 (stored)
[2026-10-07T05:17:13.822000+00:00] BTCUSDT    SELL price=84170.00000000 qty=0.00298000 id=6741801203 (stored)

Captured 5 trades.
Total trades in DB: 5

Most recent 3 trades from DB:
  2026-10-07T05:17:13.822000+00:00  BTCUSDT  SELL  84170.00000000 x 0.00298000
  2026-10-07T05:17:13.803000+00:00  BTCUSDT  BUY  84170.01000000 x 0.01239000
  2026-10-07T05:17:13.725000+00:00  BTCUSDT  SELL  84170.00000000 x 0.00246000
```

Run it again — trades are captured with `(stored)` or `(duplicate)`, and the
total count grows without ever inserting a duplicate.

## Tech stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Language   | Python 3.12+                        |
| Async I/O  | `asyncio`, `aiohttp`, `websockets`  |
| Validation | `pydantic` v2                       |
| Config     | `pydantic-settings`                 |
| Logging    | `structlog`                         |
| Storage    | SQLite via `aiosqlite`              |
| Testing    | `pytest`, `pytest-asyncio`          |
| Quality    | `ruff`, `mypy --strict`             |
| CI/CD      | GitHub Actions (Python 3.12–3.14)   |

## Project structure

```
tickstream/
├── src/tickstream/
│   ├── config.py               # pydantic-settings configuration
│   ├── schemas.py              # Trade, OrderBookLevel, OrderBookSnapshot
│   ├── exchanges/
│   │   ├── base.py             # ExchangeClient ABC
│   │   └── binance.py          # Binance WebSocket client
│   └── storage/
│       ├── base.py             # TradeRepository ABC
│       └── sqlite.py           # SQLiteTradeRepository
├── tests/unit/                 # 30 unit tests, no network required
├── scripts/live_demo.py        # End-to-end demo
├── docs/images/                # Architecture diagrams
├── .github/workflows/ci.yml    # Lint, typecheck, test on 3.12–3.14
├── .env.example
├── Makefile
├── pyproject.toml
└── README.md
```

## Development

With a virtualenv active:

```
make check    # CI mirror: lint + format-check + typecheck + test
make cov      # Run tests with coverage
make demo     # Live Binance demo
make clean    # Remove caches and local DB
```

Or run commands directly:

```
ruff check .
ruff format --check .
mypy src
pytest --cov=src/tickstream --cov-report=term-missing
```

## Testing

All 30 unit tests run offline (mocked WebSocket, in-memory-like SQLite via `tmp_path`).
CI runs the full suite against Python 3.12, 3.13, and 3.14.

| Module                       | Coverage |
|------------------------------|----------|
| `config.py`                  | 100%     |
| `schemas.py`                 | 100%     |
| `exchanges/base.py`          | 83%      |
| `exchanges/binance.py`       | 62%      |
| `storage/sqlite.py`          | 92%      |
| **Total**                    | **83%**  |

## Roadmap

- [x] Phase 1 — Binance WebSocket ingestion + SQLite persistence
- [ ] Phase 2 — Multi-exchange support (OKX, Bybit)
- [ ] Phase 3 — PostgreSQL persistence layer
- [ ] Phase 4 — Prometheus metrics + Grafana dashboard
- [ ] Phase 5 — Docker Compose + deployment guide

## Limitations

- Only trades are ingested today; order book, funding, and open interest are planned.
- SQLite is a good fit for local research; production deploys will use PostgreSQL.
- Public exchange endpoints are rate-limited; ingestion is best-effort.

## Disclaimer

This project is for research and educational purposes. It does not provide financial
advice and makes no guarantee of trading performance. Backtest results (once added)
are not indicative of future returns.

## License

MIT — see [LICENSE](LICENSE).

## Author

**Muhammad Rehan Saeed** — [GitHub](https://github.com/rehansaeedjutt-rgb)
