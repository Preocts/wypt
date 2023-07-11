from __future__ import annotations

from collections.abc import Generator
from unittest.mock import patch

import pytest

from wypt import api as api_module
from wypt.database import Database


@pytest.fixture(autouse=True)
def api(mock_database: Database) -> Generator[None, None, None]:
    # This mocks out the database with our mock database in conftest.py
    with patch.object(api_module.runtime, "get_database", return_value=mock_database):
        yield None


def test_get_table() -> None:
    with patch.object(api_module.APIHandler, "get_table_dct") as mock:
        api_module.get_table("table name", "123", 50)

    mock.assert_called_once_with("table name", "123", 50)


def test_delete_table_row() -> None:
    with patch.object(api_module.APIHandler, "delete_table_rows") as mock:
        api_module.delete_table_row("table name", "123,234")

    mock.assert_called_once_with("table name", "123,234")
