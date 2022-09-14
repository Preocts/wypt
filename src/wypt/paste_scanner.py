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
from .scanner import Scanner


class PasteScanner:
    """Gather and scan paste data from pastebin."""

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        *,
        database_file: str = "wypt_db.sqlite3",
        pattern_config_file: str = "wypt.toml",
        save_paste_content: bool = False,
    ) -> None:
        """
        Initialize connection to pastebin and database.

        Args:
            database_file: Override default sqlite3 file used
            pattern_config_file: Override default pattern toml used
            save_paste_content: When true, full paste content saved to database
        """
        dbconn = Connection(database_file)

        self._db = Database(dbconn)
        self._db.add_table("paste", "tables/paste_database_tbl.sql", Paste)
        self._db.add_table("meta", "tables/meta_database_tbl.sql", Meta)
        self._db.add_table("match", "tables/match_database_tbl.sql", Match)

        self._api = PastebinAPI()
        self._scanner = Scanner(pattern_config_file)
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
                if self._api.can_scrape:
                    self._run_scrape()
                if self._to_pull and self._api.can_scrape_item:
                    self._run_scrape_item()
        except KeyboardInterrupt:
            self.logger.info("Exiting loop process.")

    def _run_scrape(self) -> None:
        """Scrape the most recent paste meta data."""
        self.logger.debug("Pulling most recent paste meta.")
        prior_count = self._db.row_count("meta")
        results = self._api.scrape()

        if results:
            self._db.insert_many("meta", results)
            self._hydrate_to_pull()

        final_count = self._db.row_count("meta")

        self.logger.info(
            "Discovered %d - Prior count %d - Current count %d",
            len(results),
            prior_count,
            final_count,
        )

    def _run_scrape_item(self) -> None:
        """Scrape pastes from meta table that have not been collected."""
        key = self._to_pull.pop()
        result = self._api.scrape_item(key)
        if result is None:
            return

        # Matches will be a list of (match_label, match_content) values
        matches = self._scanner.scan(result.content)

        self.logger.info(
            "Paste content for key %s (size: %d) - %d matches - remaining: %d",
            key,
            len(result.content),
            len(matches),
            len(self._to_pull),
        )

        result = result if self._save_paste_content else Paste(key, "")
        self._db.insert("paste", result)
        if matches:
            self._db.insert_many("match", [Match(key, nm, val) for nm, val in matches])

    def _hydrate_to_pull(self) -> None:
        """Hydrate list of keys remaining to be pulled and scanned if empty."""
        if not self._to_pull:
            self._to_pull = self._db.get_difference("meta", "paste", limit=100)


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    gatherer = PasteScanner()
    gatherer.run()
