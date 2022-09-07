"""Scan a string for patterns of interest."""
from __future__ import annotations

import logging
import re
from pathlib import Path

import toml


class Scanner:
    """Scan a string for patterns of interest."""

    logger = logging.getLogger(__name__)

    def __init__(self, pattern_config_file: str = "wypt.toml") -> None:
        """Load and compile patterns config into scanner"""
        self._config_file = pattern_config_file
        self._filters = toml.load(Path(pattern_config_file).open())["PATTERNS"]
        self._patterns = self._compile_patterns()

    def _load_pattern_file(self) -> None:
        """Load a config file with patterns"""

    def _compile_patterns(self) -> dict[str, re.Pattern[str]]:
        """Compile patterns found in loaded config."""
        rlt: dict[str, re.Pattern[str]] = {}
        for key, value in self._filters.items():
            rlt[key] = re.compile(value)
        self.logger.debug("Compiled %d of %d filters", len(rlt), len(self._filters))
        return rlt

    def scan(self, string: str) -> dict[str, list[str]] | None:
        """
        Scan string, return dict of any matched patterns or None.

        Results will be key:pair values where the key is the pattern
        name as defined in the `wypt.toml`. Values will be a list of
        matched strings.
        """
        matches: dict[str, list[str]] = {}

        for label, pattern in self._patterns.items():
            match = pattern.findall(string)
            if match:
                matches[label] = match
        return matches if matches else None
