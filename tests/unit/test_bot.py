"""Tests for the Bot wiring and the FakeClient transport."""

from __future__ import annotations

from discord_bot_template.bot import Bot
from discord_bot_template.builtins import register_builtins
from discord_bot_template.client import FakeClient
from discord_bot_template.registry import CommandRegistry


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def _make_bot(clock: FakeClock) -> tuple[Bot, FakeClient]:
    reg = CommandRegistry(clock=clock)
    register_builtins(reg)
    client = FakeClient()
    return Bot(reg, client, channel="general"), client


def test_handle_message_sends_reply() -> None:
    bot, client = _make_bot(FakeClock())
    reply = bot.handle_message("!whoami", author="alice")
    assert reply == "You are alice."
    assert client.last() is not None
    assert client.last().channel == "general"
    assert client.last().content == "You are alice."


def test_ignored_message_sends_nothing() -> None:
    bot, client = _make_bot(FakeClock())
    assert bot.handle_message("no prefix here") is None
    assert client.sent == []


def test_unknown_command_is_friendly() -> None:
    bot, client = _make_bot(FakeClock())
    reply = bot.handle_message("!nope")
    assert reply == "Unknown command: nope"
    assert len(client.sent) == 1


def test_cooldown_reply_on_rapid_reuse() -> None:
    clock = FakeClock()
    bot, client = _make_bot(clock)

    assert bot.handle_message("!ping", author="bob") == "pong"
    clock.advance(1.0)
    reply = bot.handle_message("!ping", author="bob")
    assert reply is not None
    assert reply.startswith("Slow down!")
    # Both attempts produced an outbound message (pong + the cooldown notice).
    assert len(client.sent) == 2


def test_echo_round_trip() -> None:
    bot, _client = _make_bot(FakeClock())
    assert bot.handle_message('!echo "hello world"') == "hello world"
