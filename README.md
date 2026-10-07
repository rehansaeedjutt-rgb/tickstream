# tickstream

> A production-grade, real-time crypto market data engine.

[![CI](https://github.com/rehansaeedjutt-rgb/tickstream/actions/workflows/ci.yml/badge.svg)](https://github.com/rehansaeedjutt-rgb/tickstream/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)

## Overview

tickstream ingests real-time market data from major crypto exchanges via WebSocket
and REST APIs, normalizes it into a unified schema, and persists it for downstream
research, analytics, and risk systems.

**Status:** In active development (Phase 1: Binance WebSocket ingestion).

## Architecture

Architecture diagram will be added in docs/images/architecture.png.

## Planned Features

- [ ] Multi-exchange WebSocket ingestion (Binance, OKX, Bybit)
- [ ] Unified schema across exchanges (trades, order book, funding, open interest)
- [ ] Async reconnection with exponential backoff
- [ ] PostgreSQL persistence layer
- [ ] Structured logging (structlog)
- [ ] Pydantic-validated messages
- [ ] Prometheus-compatible metrics
- [ ] Docker + docker-compose
- [ ] GitHub Actions CI (lint, type-check, test)
- [ ] Over 80% test coverage

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12+ |
| Async I/O | asyncio, aiohttp, websockets |
| Validation | pydantic |
| Logging | structlog |
| Storage | PostgreSQL (planned) |
| Testing | pytest, pytest-asyncio |
| Quality | ruff, mypy |
| CI/CD | GitHub Actions |
| Container | Docker |

## Getting Started

### Prerequisites

- Python 3.12 or newer
- Git

### Installation

git clone https://github.com/rehansaeedjutt-rgb/tickstream.git
cd tickstream
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

## Development

ruff check .
ruff format .
mypy src
pytest --cov=src/tickstream --cov-report=term-missing

## Project Structure

src/tickstream/        Package source (src-layout)
tests/unit/            Fast, isolated tests
tests/integration/     Tests against live or fake services
docs/images/           Architecture diagrams
scripts/               Utility scripts
docker/                Dockerfiles
.github/workflows/     CI/CD

## Limitations

- Project is in early development; APIs may change.
- Public exchange endpoints are rate-limited; ingestion is best-effort.

## License

MIT - see LICENSE file.
