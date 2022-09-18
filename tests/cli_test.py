from __future__ import annotations

from unittest.mock import patch

from wypt import cli
from wypt.runtime import _Config


def test_scan() -> None:
    safe_config = _Config(database_file=":memory:")
    with patch.object(cli.runtime, "get_config", return_value=safe_config):
        with patch.object(cli.PasteScanner, "run") as mock_run:
            cli.scan()

    assert mock_run.call_count == 1
