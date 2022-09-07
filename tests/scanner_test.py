from __future__ import annotations

from wypt.scanner import Scanner

TEST_STRING = """
This is a test string
which will contain preocts.spam@someemail.com a random
bit of 555555555 interesting34583547858682157crap. Add
more to this string as more tests are a@b.c needed.
"""

EXPECTED = {
    "Basic Email": ["preocts.spam@someemail.com", "a@b.c"],
    "AMEX Card": ["345835478586821"],
}


def test_scan() -> None:
    scanner = Scanner("tests/fixture/test_filters.toml")

    result = scanner.scan(TEST_STRING)

    assert result
    for key, value in EXPECTED.items():
        assert result[key] == value


def test_scan_no_hit() -> None:
    scanner = Scanner("tests/fixture/test_filters.toml")

    result = scanner.scan("Nothing")

    assert result is None
