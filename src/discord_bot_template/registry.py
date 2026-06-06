"""Command registry: register handlers and dispatch parsed messages.

A :class:`CommandRegistry` maps command names to handler callables and
enforces a per-command cooldown using an injectable monotonic clock (so
tests can advance time deterministically). :meth:`dispatch` parses a raw
message, finds the handler, applies cooldown, and returns a response string.

Part of Discord Bot Template by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from discord_bot_template.command import ParsedCommand, parse_message


@dataclass(frozen=True, slots=True)
class Context:
    """Everything a handler needs about an incoming invocation.

    Attributes:
        author: The display name / id of the message author.
        command: The command name that was invoked.
        args: The positional arguments passed to the command.
    """

    author: str
    command: str
    args: list[str]


# A handler receives the invocation context and returns the reply text.
Handler = Callable[[Context], str]


class UnknownCommandError(LookupError):
    """Raised when a parsed command has no registered handler."""


class CooldownError(RuntimeError):
    """Raised when a command is re-used before its cooldown elapses.

    Attributes:
        retry_after: Seconds remaining until the command may be used again.
    """

    def __init__(self, command: str, retry_after: float) -> None:
        self.command = command
        self.retry_after = retry_after
        super().__init__(f"command '{command}' is on cooldown; retry in {retry_after:.2f}s")


@dataclass(slots=True)
class _Command:
    """Internal record for a registered command."""

    name: str
    handler: Handler
    cooldown: float
    help: str


class CommandRegistry:
    """Registers command handlers and dispatches messages to them.

    Args:
        prefix: The command prefix used when parsing messages.
        clock: A zero-arg callable returning monotonic seconds. Defaults to
            :func:`time.monotonic`. Inject a fake clock to control cooldowns
            in tests.
    """

    def __init__(
        self,
        prefix: str = "!",
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.prefix = prefix
        self._clock = clock
        self._commands: dict[str, _Command] = {}
        self._last_used: dict[str, float] = {}

    def register(
        self,
        name: str,
        handler: Handler,
        *,
        cooldown: float = 0.0,
        help: str = "",
    ) -> None:
        """Register ``handler`` under ``name``.

        Args:
            name: Command name (case-insensitive; stored lower-cased).
            handler: Callable invoked with a :class:`Context`.
            cooldown: Minimum seconds between successive uses (0 disables it).
            help: Short human-readable description.

        Raises:
            ValueError: If ``name`` is empty, ``cooldown`` is negative, or the
                name is already registered.
        """
        key = name.strip().lower()
        if not key:
            raise ValueError("command name must be non-empty")
        if cooldown < 0:
            raise ValueError("cooldown must be non-negative")
        if key in self._commands:
            raise ValueError(f"command '{key}' is already registered")
        self._commands[key] = _Command(key, handler, cooldown, help)

    def command(
        self, name: str, *, cooldown: float = 0.0, help: str = ""
    ) -> Callable[[Handler], Handler]:
        """Decorator form of :meth:`register`.

        Example:
            >>> reg = CommandRegistry()
            >>> @reg.command("ping")
            ... def ping(ctx: Context) -> str:
            ...     return "pong"
        """

        def decorator(handler: Handler) -> Handler:
            self.register(name, handler, cooldown=cooldown, help=help)
            return handler

        return decorator

    def names(self) -> list[str]:
        """Return the registered command names, sorted."""
        return sorted(self._commands)

    def parse(self, content: str) -> ParsedCommand | None:
        """Parse ``content`` using this registry's prefix."""
        return parse_message(content, self.prefix)

    def dispatch(self, content: str, author: str = "user") -> str | None:
        """Parse and execute ``content``, returning the handler's reply.

        Args:
            content: The raw message text.
            author: The message author, passed through to the handler.

        Returns:
            The reply string, or ``None`` if the message was not a command
            (did not start with the prefix).

        Raises:
            UnknownCommandError: If the command name is not registered.
            CooldownError: If the command is still on cooldown.
        """
        parsed = self.parse(content)
        if parsed is None:
            return None

        cmd = self._commands.get(parsed.name)
        if cmd is None:
            raise UnknownCommandError(parsed.name)

        now = self._clock()
        if cmd.cooldown > 0:
            last = self._last_used.get(cmd.name)
            if last is not None:
                elapsed = now - last
                if elapsed < cmd.cooldown:
                    raise CooldownError(cmd.name, cmd.cooldown - elapsed)

        ctx = Context(author=author, command=parsed.name, args=parsed.args)
        reply = cmd.handler(ctx)
        # Record usage only after a successful, non-cooled-down invocation.
        if cmd.cooldown > 0:
            self._last_used[cmd.name] = now
        return reply
