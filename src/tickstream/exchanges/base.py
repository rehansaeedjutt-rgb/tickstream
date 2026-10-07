"""Abstract exchange client interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from tickstream.schemas import Trade


class ExchangeClient(ABC):
    """Abstract interface every exchange client must implement.

    Concrete clients are responsible for:

    - Connecting to the exchange's WebSocket endpoint.
    - Translating the exchange's wire format into validated
      :class:`~tickstream.schemas.Trade` objects.
    - Reconnecting on transient failures with exponential backoff.
    - Yielding trades as an async iterator.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable exchange name, e.g. ``"binance"``."""
        raise NotImplementedError

    @abstractmethod
    def stream_trades(self, symbols: list[str]) -> AsyncGenerator[Trade, None]:
        """Yield validated trades for the given symbols.

        The returned async iterator must:

        - Yield only :class:`~tickstream.schemas.Trade` instances.
        - Automatically reconnect on transient errors.
        - Raise only on unrecoverable errors (e.g. invalid symbols).
        """
        raise NotImplementedError
