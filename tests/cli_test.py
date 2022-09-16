from __future__ import annotations

from unittest.mock import patch

from wypt import cli


def test_scan() -> None:
    with patch.object(cli.PasteScanner, "run") as mock_run:
        cli.scan(":memory:")

    assert mock_run.call_count == 1
