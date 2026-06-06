"""Message parsing: turn a raw chat message into a command invocation.

A message like ``"!ping arg1 arg2"`` is parsed into a :class:`ParsedCommand`
with ``name="ping"`` and ``args=["arg1", "arg2"]``, using a configurable
prefix. Messages that do not start with the prefix are ignored (``None``).

Part of Discord Bot Template by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

import shlex

from pydantic import BaseModel, Field


class ParsedCommand(BaseModel):
    """A parsed command invocation extracted from a raw message.

    Attributes:
        name: The command name, lower-cased and without the prefix.
        args: The positional arguments following the command name.
    """

    name: str
    args: list[str] = Field(default_factory=list)


def parse_message(content: str, prefix: str = "!") -> ParsedCommand | None:
    """Parse ``content`` into a :class:`ParsedCommand`, or ``None`` if ignored.

    The message is ignored (returns ``None``) when it does not start with
    ``prefix`` or when nothing but the prefix (and whitespace) is present.
    Argument splitting follows shell-like quoting rules, so
    ``'!say "hello world"'`` yields a single argument ``hello world``.

    Args:
        content: The raw message text, e.g. ``"!ping arg1 arg2"``.
        prefix: The command prefix to strip; must be non-empty.

    Returns:
        A :class:`ParsedCommand`, or ``None`` if the message is not a command.

    Raises:
        ValueError: If ``prefix`` is empty.
    """
    if not prefix:
        raise ValueError("prefix must be a non-empty string")

    if not content.startswith(prefix):
        return None

    body = content[len(prefix) :].strip()
    if not body:
        return None

    try:
        tokens = shlex.split(body)
    except ValueError:
        # Unbalanced quotes: fall back to plain whitespace splitting so a
        # malformed message never crashes the dispatcher.
        tokens = body.split()

    if not tokens:
        return None

    name, *args = tokens
    return ParsedCommand(name=name.lower(), args=args)
