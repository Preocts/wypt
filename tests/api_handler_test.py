from __future__ import annotations

import pytest

from tests.conftest import META_ROWS
from wypt.api_handler import APIHandler
from wypt.database import Database


@pytest.fixture
def handler(mock_database: Database) -> APIHandler:
    return APIHandler(mock_database)


@pytest.mark.parametrize(
    ("text", "expected"),
    (
        ("1, 2,\t 3", ["1", "2", "3"]),
        ("1,2,3", ["1", "2", "3"]),
        ("", []),
        ("1", ["1"]),
    ),
)
def test_clean_split(text: str, expected: list[str]) -> None:
    result = APIHandler._clean_split(text)
    assert result == expected


def test_get_matchview_has_results(handler: APIHandler) -> None:
    results = handler.get_matchview()

    assert results


def test_Get_matchview_has_no_results(handler: APIHandler) -> None:
    results = handler.get_matchview(0, 0)

    assert not results


def test_get_matchview_links_defaults(handler: APIHandler) -> None:
    previous_page, next_page = handler.get_matchview_params()

    assert previous_page == ""
    assert next_page == ""


def test_get_matchview_links_has_next(handler: APIHandler) -> None:
    previous_page, next_page = handler.get_matchview_params(1, 0)

    assert previous_page == ""
    assert next_page == "limit=1&offset=1"


def test_get_matchview_links_has_previous(handler: APIHandler) -> None:
    previous_page, next_page = handler.get_matchview_params(1, 1)

    assert previous_page == "limit=1&offset=0"
    assert next_page == ""


def test_get_matchview_pages_total_pages(handler: APIHandler) -> None:
    current, total = handler.get_matchview_pages(1, 0)

    assert current == "1"
    assert total == "2"


def test_get_matchview_current_page(handler: APIHandler) -> None:
    current, total = handler.get_matchview_pages(1, 1)

    assert current == "2"
    assert total == "2"


def test_delete_matchview(handler: APIHandler) -> None:
    key = META_ROWS[0].key

    success = handler.delete_matchview(key)
    failure = handler.delete_matchview("")

    assert success
    assert not failure
