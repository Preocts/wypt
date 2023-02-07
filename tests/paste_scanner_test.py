from __future__ import annotations

import re
from typing import Generator
from typing import Sequence
from unittest.mock import patch

import pytest
from wypt.model import BaseModel
from wypt.model import Meta
from wypt.model import Paste
from wypt.paste_scanner import PasteScanner


class MockPastebinAPI:
    @property
    def can_scrape(self) -> bool:
        raise NotImplementedError()

    @property
    def can_scrape_item(self) -> bool:
        raise NotImplementedError()

    def scrape(
        self,
        limit: int | None = None,
        lang: str | None = None,
        *,
        raise_on_throttle: bool = True,
    ) -> list[Meta]:
        raise NotImplementedError()

    def scrape_item(
        self,
        key: str,
        *,
        raise_on_throttle: bool = True,
    ) -> Paste | None:
        raise NotImplementedError()


class MockPatternConfig:
    def pattern_iter(self) -> Generator[tuple[str, re.Pattern[str]], None, None]:
        raise NotImplementedError()


class MockDatabase:
    def insert(self, table: str, row_data: BaseModel) -> None:
        raise NotImplementedError()

    def insert_many(self, table: str, rows: Sequence[BaseModel]) -> None:
        raise NotImplementedError()

    def get_difference(
        self, left_table: str, right_table: str, limit: int = 25
    ) -> list[str]:
        return []


@pytest.fixture
def ps() -> PasteScanner:
    return PasteScanner(MockDatabase(), MockPatternConfig(), MockPastebinAPI())


def test_run(ps: PasteScanner) -> None:
    with patch.object(ps, "_run") as mock:
        ps.run()

    assert mock.call_count == 1


def test_run_scape(ps: PasteScanner) -> None:
    with patch.object(ps._pastebin_api, "scrape", side_effect=[[], [1]]) as mock_pull:
        with patch.object(ps._database, "insert_many") as mock_db:
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
            with patch.object(ps._database, "insert") as mock_paste_db:
                with patch.object(ps._database, "insert_many") as mock_meta_db:
                    ps._run_scrape_item()

    assert mock_paste_db.call_count == 1
    assert mock_meta_db.call_count == 1


def test_run_scrape_item_without_match(ps: PasteScanner) -> None:
    ps._to_pull = ["mock"]
    paste = Paste("mock", "Hello there!")
    ptn = re.compile("^$")  # Match nothing
    with patch.object(ps._pastebin_api, "scrape_item", return_value=paste):
        with patch.object(ps._patterns, "pattern_iter", return_value=[("mock", ptn)]):
            with patch.object(ps._database, "insert") as mock_paste_db:
                with patch.object(ps._database, "insert_many") as mock_match_db:
                    ps._run_scrape_item()

    assert mock_paste_db.call_count == 1
    assert mock_match_db.call_count == 0


def test_run_scrape_early_return(ps: PasteScanner) -> None:
    ps._to_pull = ["mock"]
    with patch.object(ps._pastebin_api, "scrape_item", return_value=None):
        ps._run_scrape_item()
