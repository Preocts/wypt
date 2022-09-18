from __future__ import annotations

from sqlite3 import Connection
from unittest.mock import patch

from wypt import cli


def test_scan() -> None:
    with patch.object(cli, "Connection", return_value=Connection(":memory:")):
        with patch.object(cli.PasteScanner, "run") as mock_run:
            cli.scan()

    assert mock_run.call_count == 1
