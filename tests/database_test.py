from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from random import choice
from sqlite3 import Connection
from typing import List
from typing import Tuple

import pytest
from wypt.database import Database
from wypt.model import BaseModel
from wypt.model import Match
from wypt.model import Paste
from wypt.model import PasteMeta


METAS = Path("tests/fixture/scrape_resp.json").read_text()
PASTES = Path("tests/fixture/paste.json").read_text()
MATCHES = Path("tests/fixture/match.json").read_text()

META_ROWS = [PasteMeta(**d) for d in json.loads(METAS)]
PASTE_ROWS = [Paste(**d) for d in json.loads(PASTES)]
MATCH_ROWS = [Match(**d) for d in json.loads(MATCHES)]

TABLE_DATA = [
    ("pastemeta", META_ROWS),
    ("paste", PASTE_ROWS),
    ("match", MATCH_ROWS),
]
T_Data = Tuple[str, List[BaseModel]]


@pytest.fixture
def db() -> Database:
    dbconn = Connection(":memory:")

    database = Database(dbconn)
    database.add_table("paste", "tables/paste_database_tbl.sql", Paste)
    database.add_table("pastemeta", "tables/meta_database_tbl.sql", PasteMeta)
    database.add_table("match", "tables/match_database_tbl.sql", Match)

    return database


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

    initial = db.insert(table, row)
    duplicate = db.insert(table, row)
    row_count = db.row_count(table)

    assert initial is True
    assert duplicate is False
    assert row_count == 1


@pytest.mark.parametrize("table_data", TABLE_DATA)
def test_insert_many_with_failure(db: Database, table_data: T_Data) -> None:
    table, models = table_data
    expected_len = len(models)
    # Create new list here to prevent pollution
    models = models + [models[0]]

    results = db.insert_many(table, models)

    assert db.row_count(table) == expected_len
    assert len(results) == 1
    assert results[0] == expected_len  # Last entry is duplicate


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
    metas = [PasteMeta(**meta) for meta in json.loads(METAS)]
    paste = Paste(metas[0].key, "")
    db.insert_many("pastemeta", metas)
    db.insert("paste", paste)

    results = db.get_difference("pastemeta", "paste", limit=100)

    assert metas[0].key not in results
    assert len(results) == len(metas) - 1
