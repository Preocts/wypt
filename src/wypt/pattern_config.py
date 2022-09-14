"""Scan a string for patterns of interest."""
from __future__ import annotations

import logging
import re
from pathlib import Path

import toml


class PatternConfig:
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
            try:
                rlt[key] = re.compile(value)
            except re.error:
                self.logger.warning("Invalid pattern: %s - '%s'", key, value)
        self.logger.debug("Compiled %d of %d filters", len(rlt), len(self._filters))
        return rlt

    def scan(self, string: str) -> list[tuple[str, str]]:
        """Scan against all loaded patterns return pattern label, match if found."""
        matches: list[tuple[str, str]] = []

        for label, pattern in self._patterns.items():
            match = pattern.findall(string)
            if match:
                matches.extend([(label, m) for m in match])
        return matches
