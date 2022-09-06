"""
Gather paste meta from pastebin.
"""
from __future__ import annotations

import logging
from sqlite3 import Connection

from .meta_database import MetaDatabase
from .pastebin_api import PastebinAPI


class PasteGatherer:
    """Gather paste data from pastebin."""

    logger = logging.getLogger(__name__)

    def __init__(self, database_file: str = "wypt_db.sqlite3") -> None:
        """Initialize connection to pastebin and database."""
        dbconn = Connection(database_file)

        self._api = PastebinAPI()
        self._meta = MetaDatabase(dbconn)

    def run(self) -> None:
        """Run main gather loop. CTRL + C to exit loop."""
        self.logger.info("Starting main gather loop. Press CTRL + C to stop.")
        try:
            self._run()

        except KeyboardInterrupt:
            self.logger.info("Exiting loop process.")

    def _run(self) -> None:
        """Internal main loop."""
        while "dreams flow":
            if self._api.can_scrape:
                self._run_scrape()

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


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    gatherer = PasteGatherer()
    gatherer.run()
