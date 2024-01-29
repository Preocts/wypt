"""
Gather and scan paste data from pastebin.
"""
from __future__ import annotations

import logging

from .database import Database as _Database
from .model import Match
from .model import Paste
from .pastebin_api import PastebinAPI as _PastebinAPI
from .pattern_config import PatternConfig as _PatternConfig

PULL_PASTE_LIMIT = 100


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
            self._database.insert_metas(results)
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
        self._database.insert_paste(result)

    def _save_pattern_matches(self, key: str, content: str) -> int:
        """Save matches from content to database, return count of matches."""
        matches: list[Match] = []

        for label, pattern in self._patterns.pattern_iter():
            match = pattern.findall(content)
            if match:
                matches.extend([Match(key, label, val) for val in match])

        if matches:
            self._database.insert_matches(matches)

        return len(matches)

    def _hydrate_to_pull(self) -> None:
        """Hydrate list of keys remaining to be pulled and scanned if empty."""
        self._to_pull = self._database.get_keys_to_pull(limit=PULL_PASTE_LIMIT)
        self.logger.info("Hydration created %d keys to pull.", len(self._to_pull))
