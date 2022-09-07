"""
Gather paste meta from pastebin.
"""
from __future__ import annotations

import logging
from sqlite3 import Connection

from .meta_database import MetaDatabase
from .paste_database import PasteDatabase
from .pastebin_api import PastebinAPI


class PasteGatherer:
    """Gather paste data from pastebin."""

    logger = logging.getLogger(__name__)

    def __init__(self, database_file: str = "wypt_db.sqlite3") -> None:
        """Initialize connection to pastebin and database."""
        dbconn = Connection(database_file)

        self._api = PastebinAPI()
        self._meta = MetaDatabase(dbconn)
        self._paste = PasteDatabase(dbconn)
        self._to_pull: list[str] = []
        self._remaining_flag = False

    def run(self) -> None:
        """Run main gather loop. CTRL + C to exit loop."""
        self._hydrate_to_pull()

        self.logger.info("Starting main gather loop. Press CTRL + C to stop.")
        self.logger.info("%d keys discovered for pulling.", len(self._to_pull))
        try:
            self._run()

        except KeyboardInterrupt:
            self.logger.info("Exiting loop process.")

    def _run(self) -> None:
        """Internal main loop."""
        while "dreams flow":
            if self._api.can_scrape:
                self._run_scrape()
            if self._to_pull and self._api.can_scrape_item:
                self._run_scrape_item()

    def _run_scrape(self) -> None:
        """Scrape the most recent paste meta data."""
        self.logger.debug("Pulling most recent paste meta.")
        prior_count = self._meta.row_count
        results = self._api.scrape()

        if results:
            self._meta.insert_many(results)

        final_count = self._meta.row_count

        self.logger.info(
            "Discovered %d - Prior count %d - Current count %d",
            len(results),
            prior_count,
            final_count,
        )
        # Rehydrate to pull list
        self._hydrate_to_pull()

    def _run_scrape_item(self) -> None:
        """Scrape pastes from meta table that have not been collected."""
        key = self._to_pull.pop()

        if key:
            result = self._api.scrape_item(key)
            if result is None:
                return

            self.logger.info(
                "Downloaded paste content for key %s (size: %d) - remaining: %d",
                key,
                len(result.content),
                len(self._to_pull),
            )

            self._paste.insert(result)

    def _hydrate_to_pull(self) -> None:
        """Hydrate list of keys remaining to be pulled and scanned."""
        self._to_pull = self._meta.get_keys_to_fetch(self._meta.to_gather_count)


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    gatherer = PasteGatherer()
    gatherer.run()
