"""Bot wiring: connect a registry to a client and handle messages.

:class:`Bot` ties a :class:`~discord_bot_template.registry.CommandRegistry`
to a :class:`~discord_bot_template.client.Client`. Its
:meth:`Bot.handle_message` parses one incoming message, dispatches it, and
sends the reply (plus friendly error text for unknown commands or cooldowns)
back through the client.

Part of Discord Bot Template by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from discord_bot_template.client import Client
from discord_bot_template.registry import (
    CommandRegistry,
    CooldownError,
    UnknownCommandError,
)


class Bot:
    """A small bot that routes messages through a registry to a client.

    Args:
        registry: The command registry holding handlers and cooldowns.
        client: The transport used to deliver replies.
        channel: Default channel to send replies to.
    """

    def __init__(
        self,
        registry: CommandRegistry,
        client: Client,
        channel: str = "general",
    ) -> None:
        self.registry = registry
        self.client = client
        self.channel = channel

    def handle_message(self, content: str, author: str = "user") -> str | None:
        """Handle one incoming message end to end.

        Non-command messages (those not starting with the prefix) are ignored
        and produce no outbound message. Unknown commands and cooldown
        violations are turned into a friendly reply rather than raising.

        Args:
            content: The raw message text.
            author: The message author.

        Returns:
            The reply text that was sent, or ``None`` if the message was
            ignored.
        """
        try:
            reply = self.registry.dispatch(content, author=author)
        except UnknownCommandError as exc:
            reply = f"Unknown command: {exc.args[0]}"
        except CooldownError as exc:
            reply = f"Slow down! Try '{exc.command}' again in {exc.retry_after:.1f}s."

        if reply is None:
            return None

        self.client.send(self.channel, reply)
        return reply
