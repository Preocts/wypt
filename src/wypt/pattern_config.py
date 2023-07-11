"""Scan a string for patterns of interest."""
from __future__ import annotations

import logging
import re
from collections.abc import Generator


class PatternConfig:
    """Scan a string for patterns of interest."""

    logger = logging.getLogger(__name__)

    def __init__(self, patterns: dict[str, str]) -> None:
        """Compile patterns from labal: pattern."""
        self._patterns = self._compile_patterns(patterns)

    def _compile_patterns(self, filters: dict[str, str]) -> dict[str, re.Pattern[str]]:
        """Compile patterns found in loaded config."""
        rlt: dict[str, re.Pattern[str]] = {}
        for key, value in filters.items():
            try:
                rlt[key] = re.compile(value)
            except re.error:
                self.logger.warning("Invalid pattern: %s - '%s'", key, value)
        self.logger.debug("Compiled %d of %d filters", len(rlt), len(filters))
        return rlt

    def pattern_iter(self) -> Generator[tuple[str, re.Pattern[str]], None, None]:
        """Iterater of compliled pattern. Returns (Pattern Label, re.Pattern)"""
        yield from ((label, pattern) for label, pattern in self._patterns.items())
