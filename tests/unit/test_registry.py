"""Tests for command registration, dispatch, and cooldowns."""

from __future__ import annotations

import pytest

from discord_bot_template.registry import (
    CommandRegistry,
    Context,
    CooldownError,
    UnknownCommandError,
)


class FakeClock:
    """A controllable monotonic clock for cooldown tests."""

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_dispatch_invokes_handler_with_context() -> None:
    reg = CommandRegistry()
    reg.register("greet", lambda ctx: f"hi {ctx.author}: {','.join(ctx.args)}")
    assert reg.dispatch("!greet a b", author="alice") == "hi alice: a,b"


def test_non_command_returns_none() -> None:
    reg = CommandRegistry()
    reg.register("ping", lambda ctx: "pong")
    assert reg.dispatch("just chatting") is None


def test_unknown_command_raises() -> None:
    reg = CommandRegistry()
    with pytest.raises(UnknownCommandError):
        reg.dispatch("!missing")


def test_decorator_registration() -> None:
    reg = CommandRegistry()

    @reg.command("ping")
    def _ping(ctx: Context) -> str:
        return "pong"

    assert reg.dispatch("!ping") == "pong"
    assert reg.names() == ["ping"]


def test_duplicate_registration_raises() -> None:
    reg = CommandRegistry()
    reg.register("ping", lambda ctx: "pong")
    with pytest.raises(ValueError):
        reg.register("PING", lambda ctx: "again")


def test_cooldown_blocks_rapid_reuse() -> None:
    clock = FakeClock()
    reg = CommandRegistry(clock=clock)
    reg.register("ping", lambda ctx: "pong", cooldown=5.0)

    assert reg.dispatch("!ping") == "pong"

    clock.advance(2.0)
    with pytest.raises(CooldownError) as exc:
        reg.dispatch("!ping")
    assert exc.value.command == "ping"
    assert exc.value.retry_after == pytest.approx(3.0)


def test_cooldown_clears_after_interval() -> None:
    clock = FakeClock()
    reg = CommandRegistry(clock=clock)
    reg.register("ping", lambda ctx: "pong", cooldown=5.0)

    assert reg.dispatch("!ping") == "pong"
    clock.advance(5.0)
    assert reg.dispatch("!ping") == "pong"


def test_zero_cooldown_never_blocks() -> None:
    clock = FakeClock()
    reg = CommandRegistry(clock=clock)
    reg.register("spam", lambda ctx: "ok")
    assert reg.dispatch("!spam") == "ok"
    assert reg.dispatch("!spam") == "ok"


def test_negative_cooldown_rejected() -> None:
    reg = CommandRegistry()
    with pytest.raises(ValueError):
        reg.register("x", lambda ctx: "", cooldown=-1.0)
