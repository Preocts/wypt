from __future__ import annotations

import json
from pathlib import Path
from random import choice
from typing import Any
from typing import Sequence

import pytest
from wypt.database import Database
from wypt.meta_database import MetaDatabase
from wypt.model import BaseModel
from wypt.model import Paste
from wypt.model import PasteMeta
from wypt.paste_database import PasteDatabase


METAS = Path("tests/fixture/scrape_resp.json").read_text()
PASTES = Path("tests/fixture/paste.json").read_text()


@pytest.fixture(params=[1, 2])
def dbf(request: Any) -> tuple[Database, Sequence[BaseModel]]:
    if request.param == 2:
        return (PasteDatabase(), [Paste(**p) for p in json.loads(PASTES)])

    return (MetaDatabase(), [PasteMeta(**p) for p in json.loads(METAS)])


def test_init_creates_table(dbf: tuple[Database, Sequence[BaseModel]]) -> None:
    # Use our own query to confirm table exists.
    db = dbf[0]
    with db.cursor() as cursor:
        query = cursor.execute(f"SELECT count(*) from {db.table_name}")
        result = query.fetchone()

    assert result[0] == 0


def test_insert_row(dbf: tuple[Database, Sequence[BaseModel]]) -> None:
    db, metas = dbf
    meta = choice(metas)

    initial = db.insert(meta)
    duplicate = db.insert(meta)
    row_count = db.row_count

    assert initial is True
    assert duplicate is False
    assert row_count == 1
    assert db.contains(meta.key)


def test_insert_many_with_failure(dbf: tuple[Database, Sequence[BaseModel]]) -> None:
    db, metas = dbf
    expected_len = len(metas)
    metas.append(metas[0])  # type: ignore # create a duplicate

    results = db.insert_many(metas)

    assert db.row_count == expected_len
    assert len(results) == 1
    assert results[0] == expected_len  # Last entry is duplicate
