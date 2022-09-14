from __future__ import annotations

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
