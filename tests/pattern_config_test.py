from __future__ import annotations

import re
from typing import Any

import pytest
from wypt.pattern_config import PatternConfig

LABELS = {
    "Basic Email",
    "Master Card",
    "VISA Card",
    "Broken Pattern",
    "AMEX Card",
    "Discord Webhook",
    "JWT Token",
}
MISSING = "Broken Pattern"


@pytest.mark.parametrize(
    ("file", "logtext", "expected"),
    (
        ("tests/fixture/wypt.toml", "", LABELS),
        ("tests/fixture/wypt.toml.no.there", "config file not found", set()),
        ("tests/pattern_config_test.py", "Invalid toml format", set()),
        ("pyproject.toml", "section missing from", set()),
    ),
)
def test_load_config(caplog: Any, file: str, logtext: str, expected: set[str]) -> None:
    scanner = PatternConfig(file)

    patterns = scanner._load_config(file)
    labels = set(patterns.keys())

    assert labels == expected
    assert logtext in caplog.text


def test_pattern_iter() -> None:
    scanner = PatternConfig("tests/fixture/wypt.toml")

    labels = {label for label, _ in scanner.pattern_iter()}

    assert LABELS.difference(labels) == {MISSING}


def test_compile_patterns() -> None:
    scanner = PatternConfig()
    filters = scanner._load_config("tests/fixture/wypt.toml")

    patterns = scanner._compile_patterns(filters)

    for label, match in patterns.items():
        assert label in LABELS
        assert isinstance(match, re.Pattern)

    assert MISSING not in patterns
