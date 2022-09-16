"""WIP - Placeholder for CLI interface."""
from __future__ import annotations

import logging
from sqlite3 import Connection

from .database import Database
from .model import Match
from .model import Meta
from .model import Paste
from .paste_scanner import PasteScanner
from .pastebin_api import PastebinAPI
from .pattern_config import PatternConfig

# TODO: Create runtime init setup
logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


def scan(database_file: str = "wypt_database.sqlite3") -> int:
    """Point of entry for paste scanning."""
    # Connect to and build database
    dbconn = Connection(database_file)
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

    return 0


if __name__ == "__main__":
    raise SystemExit(scan())
