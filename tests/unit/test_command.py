"""Tests for message parsing."""

from __future__ import annotations

import pytest

from discord_bot_template.command import parse_message


def test_parses_command_and_args() -> None:
    parsed = parse_message("!ping arg1 arg2")
    assert parsed is not None
    assert parsed.name == "ping"
    assert parsed.args == ["arg1", "arg2"]


def test_command_name_is_lowercased() -> None:
    parsed = parse_message("!PING")
    assert parsed is not None
    assert parsed.name == "ping"


def test_non_prefixed_message_is_ignored() -> None:
    assert parse_message("hello there") is None


def test_bare_prefix_is_ignored() -> None:
    assert parse_message("!") is None
    assert parse_message("!   ") is None


def test_custom_prefix() -> None:
    parsed = parse_message("/roll 2d6", prefix="/")
    assert parsed is not None
    assert parsed.name == "roll"
    assert parsed.args == ["2d6"]
    # The default '!' prefix would now ignore the same content.
    assert parse_message("/roll 2d6") is None


def test_quoted_arguments_are_one_token() -> None:
    parsed = parse_message('!say "hello world" bye')
    assert parsed is not None
    assert parsed.args == ["hello world", "bye"]


def test_unbalanced_quotes_fall_back_to_whitespace_split() -> None:
    parsed = parse_message('!say "oops')
    assert parsed is not None
    assert parsed.name == "say"
    assert parsed.args == ['"oops']


def test_empty_prefix_raises() -> None:
    with pytest.raises(ValueError):
        parse_message("!ping", prefix="")
