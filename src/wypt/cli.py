"""WIP - Placeholder for CLI interface."""

from __future__ import annotations

from .paste_scanner import PasteScanner
from .runtime import Runtime

runtime = Runtime()
runtime.load_config()
runtime.set_logging()
runtime.set_database(runtime.get_config().database_file)


def scan() -> int:
    """Point of entry for paste scanning."""
    gatherer = PasteScanner(
        database=runtime.get_database(),
        patterns=runtime.get_patterns(),
        pastebin_api=runtime.get_api(),
        save_paste_content=True,
    )

    gatherer.run()

    return 0


if __name__ == "__main__":
    raise SystemExit(scan())
