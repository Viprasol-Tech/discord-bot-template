"""Transport abstraction: a ``Client`` protocol and an in-memory fake.

The framework never talks to Discord directly. Instead it depends on the
small :class:`Client` protocol (just ``send``). :class:`FakeClient` records
every outbound message in a list so demos and tests run with no network,
no tokens, and no SDK.

Part of Discord Bot Template by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class SentMessage:
    """A single outbound message captured by a client.

    Attributes:
        channel: The destination channel identifier.
        content: The message text that was sent.
    """

    channel: str
    content: str


@runtime_checkable
class Client(Protocol):
    """A minimal transport the bot uses to deliver responses.

    Implement this protocol to wire the framework to a real gateway
    (websocket, REST webhook, etc.). Only :meth:`send` is required.
    """

    def send(self, channel: str, content: str) -> None:
        """Send ``content`` to ``channel``."""
        ...


@dataclass(slots=True)
class FakeClient:
    """An in-memory :class:`Client` that records outbound messages.

    Useful for the offline demo and unit tests. Sent messages are available
    on :attr:`sent` in send order.
    """

    sent: list[SentMessage] = field(default_factory=list)

    def send(self, channel: str, content: str) -> None:
        """Record ``content`` as sent to ``channel``."""
        self.sent.append(SentMessage(channel=channel, content=content))

    def last(self) -> SentMessage | None:
        """Return the most recently sent message, or ``None`` if none."""
        return self.sent[-1] if self.sent else None

    def clear(self) -> None:
        """Discard all recorded messages."""
        self.sent.clear()
