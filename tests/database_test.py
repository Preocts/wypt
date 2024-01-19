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
    db.insert_many("match", MATCH_ROWS)
    db.insert_many("match", MATCH_ROWS)

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


def test_get_returns_uuid_and_paginate_token_functions(db: Database) -> None:
    # We are testing that we can limit a table of 2 rows to a single
    # row return value. We also take the uuid for that pagination and
    # assert we get row 2 of 2 with it.
    for paste in PASTE_ROWS:
        db.insert_paste(paste)

    row01, uuid01 = db.get("paste", limit=1)
    row02, uuid02 = db.get("paste", uuid01)

    assert len(row01) == 1
    assert len(row02) == 1
    assert row01[0] == PASTE_ROWS[0]
    assert row02[0] == PASTE_ROWS[1]
    assert uuid02 is None


def test_delete_many(mock_database: Database) -> None:
    rows, _ = mock_database.get("paste")
    keys = [row.key for row in rows]

    mock_database.delete_many("paste", keys)
    validate = mock_database.row_count("paste")

    assert rows
    assert validate == 0


def test_delete_one(mock_database: Database) -> None:
    rows, _ = mock_database.get("paste")

    mock_database.delete("paste", rows[0].key)

    assert len(rows) - mock_database.row_count("paste") == 1
