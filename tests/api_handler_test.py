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
