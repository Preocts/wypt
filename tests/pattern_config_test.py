from __future__ import annotations

from typing import Any

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


def test_load_config_expected_patterns() -> None:
    scanner = PatternConfig("tests/fixture/test_filters.toml")

    patterns = scanner._load_config("tests/fixture/test_filters.toml")
    labels = set(patterns.keys())

    assert labels == LABELS


def test_load_config_file_not_found(caplog: Any) -> None:
    scanner = PatternConfig("tests/fixture/test_filters.not.there")

    assert scanner._filters == {}
    assert "config file not found" in caplog.text


def test_load_config_file_invalid_toml(caplog: Any) -> None:
    scanner = PatternConfig("tests/pattern_config_test.py")

    assert scanner._filters == {}
    assert "Invalid toml format" in caplog.text


def test_load_config_file_key_error(caplog: Any) -> None:
    scanner = PatternConfig("pyproject.toml")

    assert scanner._filters == {}
    assert "section missing from" in caplog.text


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
