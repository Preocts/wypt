from __future__ import annotations

from unittest.mock import patch

import pytest
from wypt.model import Paste
from wypt.paste_scanner import PasteScanner

TEST_DB = ":memory:"
TEST_CONFIG = "tests/fixture/test_filters.toml"


@pytest.fixture
def ps() -> PasteScanner:
    return PasteScanner(database_file=TEST_DB, pattern_config_file=TEST_CONFIG)


def test_run(ps: PasteScanner) -> None:
    with patch.object(ps, "_run") as mock:

        ps.run()

    assert mock.call_count == 1


def test_run_scape(ps: PasteScanner) -> None:
    with patch.object(ps._api, "scrape", side_effect=[[], [1]]) as mock_pull:
        with patch.object(ps._db, "insert_many") as mock_db:
            # First call does not trigger insert to database
            ps._run_scrape()
            # Second call does trigger insert to database
            ps._run_scrape()

    assert mock_pull.call_count == 2
    assert mock_db.call_count == 1


def test_run_scrape_item_with_match(ps: PasteScanner) -> None:
    ps._to_pull = ["mock"]
    with patch.object(ps._api, "scrape_item", return_value=Paste("mock", "")):
        with patch.object(ps._scanner, "scan", return_value=[("mock", "mock")]):
            with patch.object(ps._db, "insert") as mock_paste_db:
                with patch.object(ps._db, "insert_many") as mock_meta_db:

                    ps._run_scrape_item()

    assert mock_paste_db.call_count == 1
    assert mock_meta_db.call_count == 1


def test_run_scrape_item_without_match(ps: PasteScanner) -> None:
    ps._to_pull = ["mock"]
    with patch.object(ps._api, "scrape_item", return_value=Paste("mock", "")):
        with patch.object(ps._scanner, "scan", return_value=[]):
            with patch.object(ps._db, "insert") as mock_paste_db:
                with patch.object(ps._db, "insert_many") as mock_meta_db:

                    ps._run_scrape_item()

    assert mock_paste_db.call_count == 1
    assert mock_meta_db.call_count == 0


def test_run_scrape_early_return(ps: PasteScanner) -> None:
    ps._to_pull = ["mock"]
    with patch.object(ps._api, "scrape_item", return_value=None):
        with patch.object(ps._scanner, "scan", return_value=[]):
            with patch.object(ps._db, "insert") as mock_paste_db:
                with patch.object(ps._db, "insert_many") as mock_meta_db:

                    ps._run_scrape_item()

    assert mock_paste_db.call_count == 0
    assert mock_meta_db.call_count == 0
