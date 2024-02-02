from __future__ import annotations

from unittest.mock import patch

import pytest

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


def test_get_matchview_content_offset_overflowed(handler: APIHandler) -> None:
    with patch.object(handler._database, "match_count", return_value=345):
        result = handler.get_matchview_context(100, 900)

    assert 100 == result.limit
    assert 300 == result.offset
    assert 4 == result.total_pages
    assert 4 == result.current_page
    assert 345 == result.total_rows
    assert not result.matchviews  # Mock database has only two rows


def test_get_matchview_content_offset_perfect_devision(handler: APIHandler) -> None:
    with patch.object(handler._database, "match_count", return_value=2900):
        result = handler.get_matchview_context(100, 3000)

    assert 100 == result.limit
    assert 2800 == result.offset  # Note the offset is adjusted
    assert 29 == result.total_pages
    assert 29 == result.current_page
    assert 2900 == result.total_rows
    assert not result.matchviews  # Mock database has only two rows


def test_get_matchview_content_returns_content(handler: APIHandler) -> None:
    result = handler.get_matchview_context(100, 0)

    # Given both prior tests do not return any content, we can assert the following
    # for confidence in the test.

    assert 2 == result.total_rows
    assert result.matchviews
