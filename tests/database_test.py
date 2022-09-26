from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from random import choice

import pytest
from wypt.database import Database
from wypt.model import BaseModel
from wypt.model import Meta
from wypt.model import Paste

from tests.conftest import METAS
from tests.conftest import T_Data
from tests.conftest import TABLE_DATA

# NOTE: Database fixtures in conftest.py file


@pytest.mark.parametrize("table_data", TABLE_DATA)
def test_init_creates_table(db: Database, table_data: T_Data) -> None:
    # Use our own query to confirm table exists.
    with db.cursor() as cursor:
        query = cursor.execute(f"SELECT count(*) from {table_data[0]}")
        result = query.fetchone()

    assert result[0] == 0


@pytest.mark.parametrize("table_data", TABLE_DATA)
def test_insert_row(db: Database, table_data: T_Data) -> None:
    table = table_data[0]
    row = choice(table_data[1])

    db.insert(table, row)
    db.insert(table, row)
    row_count = db.row_count(table)

    assert row_count == 1


@pytest.mark.parametrize("table_data", TABLE_DATA)
def test_insert_many_with_failure(db: Database, table_data: T_Data) -> None:
    table, models = table_data
    expected_len = len(models)
    # Create new list here to prevent pollution
    models = models + [models[0]]

    db.insert_many(table, models)

    assert db.row_count(table) == expected_len


@pytest.mark.parametrize("table_data", TABLE_DATA)
def test_get_iter(db: Database, table_data: T_Data) -> None:
    table, models = table_data
    db.insert_many(table, models)

    row_results: list[BaseModel] = []
    for row in db.get_iter(table, limit=1):
        row_results.append(row)

    for (model, result) in zip(models, row_results):
        assert model == result


@pytest.mark.parametrize("table_data", TABLE_DATA)
def test_to_stdout(db: Database, table_data: T_Data) -> None:
    table, models = table_data
    capture = StringIO()
    # This, ideally, should not duplicate the insert_many test but here we are :(
    expected_len = len(models)
    db.insert_many(table, models)

    with redirect_stdout(capture):
        db.to_stdout(table)

    lines = [line for line in capture.getvalue().split("\n") if line]
    assert len(lines) == expected_len


def test_metadb_get_keys_to_fetch(db: Database) -> None:
    # Setup two databases with mock data. Results should expect
    # all keys of meta fixture to be returns sans 0th index key.
    metas = [Meta(**meta) for meta in json.loads(METAS)]
    paste = Paste(metas[0].key, "")
    db.insert_many("meta", metas)
    db.insert("paste", paste)

    results = db.get_difference("meta", "paste", limit=100)

    assert metas[0].key not in results
    assert len(results) == len(metas) - 1


def test_table_guard_raises(db: Database) -> None:
    with pytest.raises(KeyError):
        db._table_guard("nothere")


def test_max_id(db: Database) -> None:
    result = db.max_id("paste")

    assert result == 0


def test_get_return_uuid_and_paginates(db: Database) -> None:
    rows_insert = [Paste("abc", "test1"), Paste("zyx", "test2")]
    db.insert_many("paste", rows_insert)

    row01, uuid1 = db.get("paste", limit=1)
    row02, uuid2 = db.get("paste", uuid1)

    assert len(row01) == 1
    assert len(row02) == 1
    assert row01[0] == rows_insert[0]
    assert row02[0] == rows_insert[1]
    assert uuid2 is None


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
