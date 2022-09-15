from __future__ import annotations

from typing import Any

import pytest
from wypt.pattern_config import PatternConfig

TEST_STRING = """
This is a test string
which will contain preocts.spam@someemail.com a random
bit of 555555555 interesting 345835478586821 crap. Add
more to this string as more tests are a@b.c needed.
"""

EXPECTED = [
    ("Basic Email", "preocts.spam@someemail.com"),
    ("Basic Email", "a@b.c"),
    ("AMEX Card", "345835478586821"),
]

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
        ("tests/fixture/test_filters.toml", "", LABELS),
        ("tests/fixture/test_filters.toml.no.there", "config file not found", set()),
        ("tests/pattern_config_test.py", "Invalid toml format", set()),
        ("tests/pyproject.toml", "section missing from", set()),
    ),
)
def test_load_config(caplog: Any, file: str, logtext: str, expected: set[str]) -> None:
    scanner = PatternConfig(file)

    patterns = scanner._load_config(file)
    labels = set(patterns.keys())

    assert labels == expected


def test_scan() -> None:
    scanner = PatternConfig("tests/fixture/test_filters.toml")

    results = scanner.scan(TEST_STRING)

    assert results

    for value in EXPECTED:
        assert value in results


def test_scan_no_hit() -> None:
    scanner = PatternConfig("tests/fixture/test_filters.toml")

    result = scanner.scan("Nothing")

    assert result == []
