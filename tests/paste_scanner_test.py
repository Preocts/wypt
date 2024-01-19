from __future__ import annotations

import re
from unittest.mock import patch

import pytest

from wypt.database import Database
from wypt.model import Paste
from wypt.paste_scanner import PasteScanner
from wypt.pastebin_api import PastebinAPI
from wypt.pattern_config import PatternConfig


@pytest.fixture
def ps(db: Database) -> PasteScanner:
    return PasteScanner(db, PatternConfig({}), PastebinAPI())


def test_run(ps: PasteScanner) -> None:
    with patch.object(ps, "_run") as mock:
        ps.run()

    assert mock.call_count == 1


def test_run_scape(ps: PasteScanner) -> None:
    with patch.object(ps._pastebin_api, "scrape", side_effect=[[], [1]]) as mock_pull:
        with patch.object(ps._database, "insert_metas") as mock_db:
            # First call does not trigger insert to database
            ps._run_scrape()
            # Second call does trigger insert to database
            ps._run_scrape()

    assert mock_pull.call_count == 2
    assert mock_db.call_count == 1


def test_run_scrape_item_with_match(ps: PasteScanner) -> None:
    ps._to_pull = ["mock"]
    paste = Paste("mock", "Hello there!")
    ptn = re.compile(".+")  # Match everything
    with patch.object(ps._pastebin_api, "scrape_item", return_value=paste):
        with patch.object(ps._patterns, "pattern_iter", return_value=[("mock", ptn)]):
            with patch.object(ps._database, "insert_paste") as mock_paste_db:
                with patch.object(ps._database, "insert_matches") as mock_match_db:
                    ps._run_scrape_item()

    assert mock_paste_db.call_count == 1
    assert mock_match_db.call_count == 1


def test_run_scrape_item_without_match(ps: PasteScanner) -> None:
    ps._to_pull = ["mock"]
    paste = Paste("mock", "Hello there!")
    ptn = re.compile("^$")  # Match nothing
    with patch.object(ps._pastebin_api, "scrape_item", return_value=paste):
        with patch.object(ps._patterns, "pattern_iter", return_value=[("mock", ptn)]):
            with patch.object(ps._database, "insert_paste") as mock_paste_db:
                with patch.object(ps._database, "insert_matches") as mock_match_db:
                    ps._run_scrape_item()

    assert mock_paste_db.call_count == 1
    assert mock_match_db.call_count == 0


def test_run_scrape_early_return(ps: PasteScanner) -> None:
    ps._to_pull = ["mock"]
    with patch.object(ps._pastebin_api, "scrape_item", return_value=None):
        ps._run_scrape_item()
