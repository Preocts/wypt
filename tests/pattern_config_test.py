from __future__ import annotations

import re

from wypt.pattern_config import PatternConfig

PATTERNS = {
    "Basic Email": '\\b[^@{}\\" ]+@[^@{}\\" ]+\\.[^@{}\\" ]+\\b',
    "Broken Pattern": "\\z",
    "Discord Webhook": "discord\\.com/api/webhooks/\\d*/.+\\b",
    "JWT Token": "[\\w-]{24}\\.[\\w-]{6}\\.[\\w-]{25,110}",
}
MISSING = "Broken Pattern"


def test_load_config() -> None:
    scanner = PatternConfig(PATTERNS)

    labels = set(scanner._patterns.keys())

    assert labels != set(list(PATTERNS.keys()))


def test_load_empty() -> None:
    scanner = PatternConfig({})

    assert scanner._patterns == {}


def test_pattern_iter() -> None:
    scanner = PatternConfig(PATTERNS)

    labels = {label for label, _ in scanner.pattern_iter()}

    assert set(PATTERNS.keys()).difference(labels) == {MISSING}


def test_compile_patterns() -> None:
    scanner = PatternConfig(PATTERNS)

    patterns = scanner._compile_patterns(PATTERNS)

    for label, match in patterns.items():
        assert label in PATTERNS
        assert isinstance(match, re.Pattern)

    assert MISSING not in patterns
