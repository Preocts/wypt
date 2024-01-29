from __future__ import annotations

import pytest

from tests.conftest import MATCH_ROWS
from tests.conftest import META_ROWS
from tests.conftest import PASTE_ROWS
from tests.conftest import TABLES
from wypt.database import Database
from wypt.model import Paste


@pytest.mark.parametrize("table", TABLES)
def test_init_creates_table(db: Database, table: str) -> None:
    with db.cursor() as cursor:
        query = cursor.execute(f"SELECT count(*) from {table}")
        result = query.fetchone()

    assert result[0] == 0


def test_insert_many_meta_rows_ignores_constraint_errors(db: Database) -> None:
    # Insert twice to confirm constraint violations are ignored
    db.insert_metas(META_ROWS)
    db.insert_metas(META_ROWS)

    assert db.row_count("meta") == len(META_ROWS)


def test_insert_many_match_rows_ignores_constraint_errors(db: Database) -> None:
    # Insert twice to confirm constraint violations are ignored
    db.insert_matches(MATCH_ROWS)
    db.insert_matches(MATCH_ROWS)

    assert db.row_count("match") == len(MATCH_ROWS)


def test_insert_one_paste_row_ignores_constraint_errors(db: Database) -> None:
    # Insert twice to confirm constraint violations are ignored
    db.insert_paste(PASTE_ROWS[0])
    db.insert_paste(PASTE_ROWS[0])

    assert db.row_count("paste") == 1


def test_metadb_get_keys_to_fetch(db: Database) -> None:
    # Setup two databases with mock data. Results should expect
    # all keys of meta fixture to be returns sans 0th index key.
    paste = Paste(META_ROWS[0].key, "")
    db.insert_metas(META_ROWS)
    db.insert_paste(paste)

    results = db.get_difference("meta", "paste", limit=100)

    assert META_ROWS[0].key not in results
    assert len(results) == len(META_ROWS) - 1


def test_table_guard_raises(db: Database) -> None:
    with pytest.raises(KeyError):
        db._table_guard("nothere")


def test_max_id(mock_database: Database) -> None:
    result = mock_database.max_id("paste")

    assert result == len(PASTE_ROWS)


def test_get_match_views(mock_database: Database) -> None:
    rows = mock_database.get_match_views()

    assert len(rows) == len(MATCH_ROWS)


def test_get_match_views_returns_offset(mock_database: Database) -> None:
    rows = mock_database.get_match_views(1, 1)

    assert len(rows) == 1
    assert rows[0].key == MATCH_ROWS[1].key


def test_get_match_views_returns_empty_over_offset(mock_database: Database) -> None:
    rows = mock_database.get_match_views(offset=100)

    assert not rows


def test_get_total_matches(mock_database: Database) -> None:
    count = mock_database.match_count()

    assert count == len(MATCH_ROWS)
