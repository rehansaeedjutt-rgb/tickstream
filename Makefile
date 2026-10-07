# tickstream developer Makefile.
# All commands assume the project virtualenv is active.

.PHONY: help install lint format typecheck test cov check demo clean

help:
	@echo "Available targets:"
	@echo "  install     Install package in editable mode with dev extras"
	@echo "  lint        Run ruff check"
	@echo "  format      Apply ruff formatting"
	@echo "  typecheck   Run mypy in strict mode"
	@echo "  test        Run pytest"
	@echo "  cov         Run pytest with coverage report"
	@echo "  check       Run lint + format-check + typecheck + test (CI mirror)"
	@echo "  demo        Run the live Binance demo (requires network)"
	@echo "  clean       Remove caches, build artifacts, and local DB"

install:
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev]"

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy src

test:
	pytest

cov:
	pytest --cov=src/tickstream --cov-report=term-missing

check: lint
	ruff format --check .
	mypy src
	pytest --cov=src/tickstream --cov-report=term-missing

demo:
	python scripts/live_demo.py

clean:
	Remove-Item -Recurse -Force -ErrorAction SilentlyContinue .pytest_cache, .ruff_cache, .mypy_cache, htmlcov, .coverage
	Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
	Remove-Item -Force -ErrorAction SilentlyContinue tickstream.db
