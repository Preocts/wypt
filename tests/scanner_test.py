from __future__ import annotations

from wypt.scanner import Scanner

TEST_STRING = """
This is a test string
which will contain preocts.spam@someemail.com a random
bit of 555555555 interesting 4234876212341224 crap. Add
more to this string as more tests are needed.
"""

EXPECTED = {
    "Basic Email": ["preocts.spam@someemail.com"],
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
