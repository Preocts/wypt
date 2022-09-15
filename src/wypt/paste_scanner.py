"""
Gather and scan paste data from pastebin.
"""
from __future__ import annotations

import logging
from sqlite3 import Connection

from .database import Database
from .model import Match
from .model import Meta
from .model import Paste
from .pastebin_api import PastebinAPI
from .pattern_config import PatternConfig


class PasteScanner:
    """Gather and scan paste data from pastebin."""

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        database: Database,
        patterns: PatternConfig,
        pastebin_api: PastebinAPI,
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
            result = self._database.insert_many("meta", results)
            self.logger.info("Discovered %d metas.", len(results) - len(result))
            self._hydrate_to_pull()

    def _run_scrape_item(self) -> None:
        """Scrape pastes from meta table that have not been collected."""
        key = self._to_pull.pop()
        result = self._pastebin_api.scrape_item(key)
        if result is None:
            return

        # Matches will be a list of (match_label, match_content) values
        matches = self._patterns.scan(result.content)

        self.logger.info(
            "Paste content for key %s (size: %d) - %d matches - remaining: %d",
            key,
            len(result.content),
            len(matches),
            len(self._to_pull),
        )

        result = result if self._save_paste_content else Paste(key, "")
        self._database.insert("paste", result)
        if matches:
            self._database.insert_many(
                "match", [Match(key, nm, val) for nm, val in matches]
            )

    def _hydrate_to_pull(self) -> None:
        """Hydrate list of keys remaining to be pulled and scanned if empty."""
        self._to_pull = self._database.get_difference("meta", "paste", limit=100)


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")

    # Connect to and build database
    dbconn = Connection("wypt_datebase.sqlite3")
    database = Database(dbconn)
    database.add_table("paste", "tables/paste_database_tbl.sql", Paste)
    database.add_table("meta", "tables/meta_database_tbl.sql", Meta)
    database.add_table("match", "tables/match_database_tbl.sql", Match)

    # Load pattern file
    pattern_config = PatternConfig()

    # Create API client
    api = PastebinAPI()

    # Create controller
    gatherer = PasteScanner(database, pattern_config, api, save_paste_content=True)

    gatherer.run()
