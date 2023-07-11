from __future__ import annotations

import pytest

from wypt.api_handler import APIHandler
from wypt.database import Database


@pytest.fixture
def handler(mock_database: Database) -> APIHandler:
    return APIHandler(mock_database)


def test_get_table_dct_next(handler: APIHandler) -> None:
    result = handler.get_table_dct("meta", None, limit=1)

    assert len(result["rows"]) == 1
    assert result["next"] is not None


def test_get_table_dct_no_next(handler: APIHandler) -> None:
    result = handler.get_table_dct("meta", None)

    assert result["next"] is None


def test_delete_rows(handler: APIHandler) -> None:
    result = handler.delete_table_rows("paste", "abc, egf")

    assert result == {}


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
