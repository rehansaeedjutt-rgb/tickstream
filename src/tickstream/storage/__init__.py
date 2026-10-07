"""Trade persistence layer."""

from tickstream.storage.base import TradeRepository
from tickstream.storage.sqlite import SQLiteTradeRepository

__all__ = ["SQLiteTradeRepository", "TradeRepository"]
