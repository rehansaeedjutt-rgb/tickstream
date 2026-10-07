# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copy only what the package build needs (better layer caching)
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

RUN python -m pip install --upgrade pip && \
    python -m pip install .

# Runtime non-root user
RUN useradd --create-home --shell /bin/bash tickstream && \
    mkdir -p /data && \
    chown -R tickstream:tickstream /app /data

USER tickstream

# Default DB location inside the container
ENV TICKSTREAM_DEMO_DB=/data/tickstream.db

# Healthcheck: import the package to prove it loaded
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import tickstream; assert tickstream.__version__" || exit 1

CMD ["python", "-m", "tickstream", "--help"]
