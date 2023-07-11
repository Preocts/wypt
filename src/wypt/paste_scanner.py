"""
Gather and scan paste data from pastebin.
"""
from __future__ import annotations

import logging
import re
from collections.abc import Generator
from collections.abc import Sequence

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore


from .model import BaseModel
from .model import Match
from .model import Meta
from .model import Paste


class _Database(Protocol):
    def insert(self, table: str, row_data: BaseModel) -> None:
        ...

    def insert_many(self, table: str, rows: Sequence[BaseModel]) -> None:
        ...

    def get_difference(
        self, left_table: str, right_table: str, limit: int = 25
    ) -> list[str]:
        ...


class _PatternConfig(Protocol):
    def pattern_iter(self) -> Generator[tuple[str, re.Pattern[str]], None, None]:
        ...


class _PastebinAPI(Protocol):
    @property
    def can_scrape(self) -> bool:
        ...

    @property
    def can_scrape_item(self) -> bool:
        ...

    def scrape(
        self,
        limit: int | None = None,
        lang: str | None = None,
        *,
        raise_on_throttle: bool = True,
    ) -> list[Meta]:
        ...

    def scrape_item(
        self,
        key: str,
        *,
        raise_on_throttle: bool = True,
    ) -> Paste | None:
        ...


class PasteScanner:
    """Gather and scan paste data from pastebin."""

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        database: _Database,
        patterns: _PatternConfig,
        pastebin_api: _PastebinAPI,
        *,
        save_paste_content: bool = False,
    ) -> None:
        """
        Initialize PasteScanner controller class.

        Args:
            database: Database provider with added tables
            patterns: PatternConfig provider
            pastebin_api: PastebinAPI provider
            save_paste_content: When true, full paste content saved to database
        """
        self._database = database
        self._patterns = patterns

        self._pastebin_api = pastebin_api

        self._to_pull: list[str] = []
        self._save_paste_content = save_paste_content

    def run(self) -> None:
        """Run main gather loop. CTRL + C to exit loop."""
        self._hydrate_to_pull()

        self.logger.info("Starting main gather loop. Press CTRL + C to stop.")
        self.logger.info("%d keys discovered for pulling.", len(self._to_pull))
        self._run()

    def _run(self) -> None:  # pragma: no cover
        """Internal main event loop."""
        try:
            while "dreams flow":
                if self._pastebin_api.can_scrape:
                    self._run_scrape()
                if self._to_pull and self._pastebin_api.can_scrape_item:
                    self._run_scrape_item()
        except KeyboardInterrupt:
            self.logger.info("Exiting loop process.")

    def _run_scrape(self) -> None:
        """Scrape the most recent paste meta data."""
        self.logger.debug("Pulling most recent paste meta.")
        results = self._pastebin_api.scrape()

        if results:
            self._database.insert_many("meta", results)
            self.logger.info("Discovered %d meta rows, stored new.", len(results))
            self._hydrate_to_pull()

    def _run_scrape_item(self) -> None:
        """Scrape pastes from meta table that have not been collected."""
        key = self._to_pull.pop()
        result = self._pastebin_api.scrape_item(key)
        if result is None:
            return

        match_count = self._save_pattern_matches(key, result.content)

        self.logger.info(
            "Paste content for key %s (size: %d) - %d matches - remaining: %d",
            key,
            len(result.content),
            match_count,
            len(self._to_pull),
        )

        # Remove content from model if class flag is False
        result = result if self._save_paste_content else Paste(key, "")
        self._database.insert("paste", result)

    def _save_pattern_matches(self, key: str, content: str) -> int:
        """Save matches from content to database, return count of matches."""
        matches: list[Match] = []

        for label, pattern in self._patterns.pattern_iter():
            match = pattern.findall(content)
            if match:
                matches.extend([Match(key, label, val) for val in match])

        if matches:
            self._database.insert_many("match", matches)

        return len(matches)

    def _hydrate_to_pull(self) -> None:
        """Hydrate list of keys remaining to be pulled and scanned if empty."""
        self._to_pull = self._database.get_difference("meta", "paste", limit=100)
