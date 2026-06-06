"""A few ready-made command handlers used by the demo and as examples.

These show the handler signature ``(Context) -> str`` and how to register a
small command set on a :class:`~discord_bot_template.registry.CommandRegistry`.

Part of Discord Bot Template by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

from discord_bot_template.registry import CommandRegistry, Context, Handler


def ping(ctx: Context) -> str:
    """Reply ``pong`` (optionally echoing trailing arguments)."""
    suffix = f" {' '.join(ctx.args)}" if ctx.args else ""
    return f"pong{suffix}"


def echo(ctx: Context) -> str:
    """Echo back whatever arguments were provided."""
    return " ".join(ctx.args) if ctx.args else "(nothing to echo)"


def whoami(ctx: Context) -> str:
    """Report the author of the message."""
    return f"You are {ctx.author}."


def make_help(registry: CommandRegistry) -> Handler:
    """Return a ``help`` handler bound to ``registry``'s command names."""

    def help_command(ctx: Context) -> str:
        return "Commands: " + ", ".join(registry.names())

    return help_command


def register_builtins(registry: CommandRegistry) -> None:
    """Register ``ping``, ``echo``, ``whoami``, and ``help`` on ``registry``.

    ``ping`` carries a small cooldown to demonstrate rate-limiting.
    """
    registry.register("ping", ping, cooldown=3.0, help="Health check.")
    registry.register("echo", echo, help="Echo your arguments back.")
    registry.register("whoami", whoami, help="Show who you are.")
    registry.register("help", make_help(registry), help="List commands.")
