from __future__ import annotations

from collections.abc import Generator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from wypt import api as api_module
from wypt.database import Database


@pytest.fixture(autouse=True)
def api(mock_database: Database) -> Generator[None, None, None]:
    # This mocks out the database with our mock database in conftest.py
    with patch.object(api_module.runtime, "get_database", return_value=mock_database):
        yield None


def test_route_favicon() -> None:
    result = api_module.favicon()

    assert result.media_type == "image/vnd.microsoft.icon"


def test_route_index() -> None:
    result = api_module.index(MagicMock())

    assert result.media_type == "text/html"


def test_route_gridsample() -> None:
    result = api_module.gridsample(MagicMock())

    assert result.media_type == "text/html"
