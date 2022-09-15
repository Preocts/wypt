"""Scan a string for patterns of interest."""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Generator

import toml


class PatternConfig:
    """Scan a string for patterns of interest."""

    logger = logging.getLogger(__name__)

    def __init__(self, pattern_config_file: str = "wypt_patterns.toml") -> None:
        """Load and compile patterns config."""
        filters = self._load_config(pattern_config_file)
        self._patterns = self._compile_patterns(filters)

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

    def _load_config(self, fp: str) -> dict[str, str]:
        """Load toml file or return empty dict on failure."""
        try:
            return toml.load(Path(fp).open())["PATTERNS"]

        except KeyError:
            self.logger.error("[PATTERNS] section missing from %s", fp)

        except FileNotFoundError:
            self.logger.error("Pattern config file not found: '%s'", fp)

        except toml.TomlDecodeError as err:
            self.logger.error("Invalid toml format in %s - '%s'", fp, err)

        return {}

    def pattern_iter(self) -> Generator[tuple[str, re.Pattern[str]], None, None]:
        """Iterater of compliled pattern. Returns (Pattern Label, re.Pattern)"""
        yield from ((label, pattern) for label, pattern in self._patterns.items())

    def scan(self, string: str) -> list[tuple[str, str]]:
        """Scan against all loaded patterns return pattern label, match if found."""
        matches: list[tuple[str, str]] = []

        for label, pattern in self._patterns.items():
            match = pattern.findall(string)
            if match:
                matches.extend([(label, m) for m in match])
        return matches
