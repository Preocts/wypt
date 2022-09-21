"""WIP - Placeholder for CLI interface."""
from __future__ import annotations

from .paste_scanner import PasteScanner
from .runtime import Runtime

runtime = Runtime()
runtime.load_config()
runtime.set_logging()


def scan() -> int:
    """Point of entry for paste scanning."""
    config = runtime.get_config()

    gatherer = PasteScanner(
        database=runtime.connect_database(config.database_file),
        patterns=runtime.get_patterns(),
        pastebin_api=runtime.get_api(),
        save_paste_content=True,
    )

    gatherer.run()

    return 0


if __name__ == "__main__":
    raise SystemExit(scan())
