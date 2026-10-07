"""Abstract trade repository interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from tickstream.schemas import Trade


class TradeRepository(ABC):
    """Abstract contract for persisting and querying trades.

    Implementations must be idempotent on ``save_trades``: saving the
    same trade twice must not create duplicates.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Create tables and indexes if they do not already exist."""

    @abstractmethod
    async def save_trades(self, trades: Sequence[Trade]) -> int:
        """Persist trades. Returns the number of newly inserted rows."""

    @abstractmethod
    async def count_trades(self) -> int:
        """Return the total number of stored trades."""

    @abstractmethod
    async def fetch_recent(self, limit: int = 10) -> list[Trade]:
        """Return the most recent trades, ordered by timestamp descending."""

    @abstractmethod
    async def close(self) -> None:
        """Release underlying resources."""
