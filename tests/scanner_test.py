from __future__ import annotations

from wypt.model import Match
from wypt.scanner import Scanner

TEST_STRING = """
This is a test string
which will contain preocts.spam@someemail.com a random
bit of 555555555 interesting 345835478586821 crap. Add
more to this string as more tests are a@b.c needed.
"""

EXPECTED = [
    Match("test", "Basic Email", str(["preocts.spam@someemail.com", "a@b.c"])),
    Match("test", "AMEX Card", str(["345835478586821"])),
]


def test_scan() -> None:
    scanner = Scanner("tests/fixture/test_filters.toml")

    results = scanner.scan("test", TEST_STRING)

    assert results

    for value in EXPECTED:
        assert value in results


def test_scan_no_hit() -> None:
    scanner = Scanner("tests/fixture/test_filters.toml")

    result = scanner.scan("test", "Nothing")

    assert result == []
