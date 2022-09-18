"""WIP - Placeholder for CLI interface."""
from __future__ import annotations

from .paste_scanner import PasteScanner
from .pastebin_api import PastebinAPI
from .pattern_config import PatternConfig
from .runtime import Runtime

runtime = Runtime()
runtime.load_config()
runtime.set_logging()


def scan() -> int:
    """Point of entry for paste scanning."""
    # Connect to and build database
    config = runtime.get_config()
    database = runtime.connect_database(config.database_file)

    # Load pattern file
    pattern_config = PatternConfig(runtime.get_config().pattern_file)

    # Create API client
    api = PastebinAPI()

    # Create controller
    gatherer = PasteScanner(
        database=database,
        patterns=pattern_config,
        pastebin_api=api,
        save_paste_content=True,
    )

    gatherer.run()

    return 0


if __name__ == "__main__":
    raise SystemExit(scan())
