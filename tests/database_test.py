from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from random import choice
from sqlite3 import Connection
from typing import Any
from typing import Sequence

import pytest
from wypt.database import Database
from wypt.database import MatchDatabase
from wypt.database import MetaDatabase
from wypt.database import PasteDatabase
from wypt.model import BaseModel
from wypt.model import Match
from wypt.model import Paste
from wypt.model import PasteMeta


METAS = Path("tests/fixture/scrape_resp.json").read_text()
PASTES = Path("tests/fixture/paste.json").read_text()
MATCHES = Path("tests/fixture/match.json").read_text()


@pytest.fixture(params=[1, 2, 3])
def dbf(request: Any) -> tuple[Database, Sequence[BaseModel]]:
    dbconn = Connection(":memory:")
    if request.param == 2:
        return (PasteDatabase(dbconn), [Paste(**p) for p in json.loads(PASTES)])
    elif request.param == 3:
        return (MatchDatabase(dbconn), [Match(**p) for p in json.loads(MATCHES)])

    return (MetaDatabase(dbconn), [PasteMeta(**p) for p in json.loads(METAS)])


def test_init_creates_table(dbf: tuple[Database, Sequence[BaseModel]]) -> None:
    # Use our own query to confirm table exists.
    db = dbf[0]
    with db.cursor() as cursor:
        query = cursor.execute(f"SELECT count(*) from {db.table_name}")
        result = query.fetchone()

    assert result[0] == 0


def test_insert_row(dbf: tuple[Database, Sequence[BaseModel]]) -> None:
    db, models = dbf
    meta = choice(models)

    initial = db.insert(meta)
    duplicate = db.insert(meta)
    row_count = db.row_count

    assert initial is True
    assert duplicate is False
    assert row_count == 1
    assert db.contains(meta.key)


def test_insert_many_with_failure(dbf: tuple[Database, Sequence[BaseModel]]) -> None:
    db, models = dbf
    expected_len = len(models)
    models.append(models[0])  # type: ignore # create a duplicate

    results = db.insert_many(models)

    assert db.row_count == expected_len
    assert len(results) == 1
    assert results[0] == expected_len  # Last entry is duplicate


def test_get_iter(dbf: tuple[Database, Sequence[BaseModel]]) -> None:
    db, models = dbf
    db.insert_many(models)

    row_results: list[BaseModel] = []
    for row in db.get_iter(limit=1):
        row_results.append(row)

    for (model, result) in zip(models, row_results):
        assert model == result


def test_to_stdout(dbf: tuple[Database, Sequence[BaseModel]]) -> None:
    db, models = dbf
    capture = StringIO()
    # This, ideally, should not duplicate the insert_many test but here we are :(
    expected_len = len(models)
    models.append(models[0])  # type: ignore # create a duplicate
    db.insert_many(models)

    with redirect_stdout(capture):
        db.to_stdout()

    lines = [line for line in capture.getvalue().split("\n") if line]
    assert len(lines) == expected_len


def test_metadb_get_keys_to_fetch() -> None:
    # Overly complex setup joyness
    # Setup two databases with mock data. Results should expect
    # all keys of meta fixture to be returns sans 0th index key.
    conn = Connection(":memory:")
    pastedb = PasteDatabase(conn)
    metadb = MetaDatabase(conn)
    metas = [PasteMeta(**meta) for meta in json.loads(METAS)]
    paste = Paste(metas[0].key, "")
    metadb.insert_many(metas)
    pastedb.insert(paste)

    results = metadb.get_keys_to_fetch()
    print(results)

    assert metas[0].key not in results
    assert len(results) == len(metas) - 1
    assert metadb.to_gather_count == len(results)
