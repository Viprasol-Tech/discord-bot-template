"""Command-line interface for Discord Bot Template.

``discord-bot-template demo`` wires a registry of built-in commands to a
:class:`~discord_bot_template.client.FakeClient` and feeds it a handful of
messages — no Discord token, no network, no SDK.

Part of Discord Bot Template by Viprasol Tech Private Limited (https://viprasol.com).
"""

from __future__ import annotations

import typer
from rich.console import Console

from discord_bot_template import __version__
from discord_bot_template.bot import Bot
from discord_bot_template.builtins import register_builtins
from discord_bot_template.client import FakeClient
from discord_bot_template.registry import CommandRegistry

app = typer.Typer(add_completion=False, help="Discord Bot Template — by Viprasol Tech.")
console = Console()

# Scripted conversation for the demo. The duplicate '!ping' exercises the
# cooldown path; the '!nope' exercises the unknown-command path; the plain
# 'hello there' (no prefix) is ignored.
_DEMO_MESSAGES: tuple[tuple[str, str], ...] = (
    ("alice", "!ping"),
    ("alice", "!ping again"),
    ("bob", "hello there"),
    ("bob", '!echo "hello world"'),
    ("carol", "!whoami"),
    ("carol", "!help"),
    ("dave", "!nope"),
)


@app.command()
def version() -> None:
    """Print the installed version."""
    console.print(f"discord-bot-template [bold cyan]{__version__}[/] — by Viprasol Tech")


@app.command()
def demo(prefix: str = typer.Option("!", help="Command prefix.")) -> None:
    """Run a scripted offline conversation through the bot."""
    # A deterministic fake clock so the cooldown demo is reproducible. Each
    # message advances virtual time by 1 second; 'ping' has a 3s cooldown, so
    # two back-to-back pings collide.
    ticks = iter(range(10_000))

    def clock() -> float:
        return float(next(ticks))

    registry = CommandRegistry(prefix=prefix, clock=clock)
    register_builtins(registry)
    client = FakeClient()
    bot = Bot(registry, client, channel="general")

    for author, content in _DEMO_MESSAGES:
        reply = bot.handle_message(content, author=author)
        if reply is None:
            console.print(f"[dim]{author}: {content}[/]  ->  [dim](ignored)[/]")
        else:
            console.print(f"{author}: {content}  ->  [bold green]{reply}[/]")

    console.print(f"\nSent [bold]{len(client.sent)}[/] messages via FakeClient.")


if __name__ == "__main__":
    app()
