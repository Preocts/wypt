from __future__ import annotations

import json
from pathlib import Path
from random import choice

import pytest
from wypt.meta_database import MetaDatabase
from wypt.model import PasteMeta


METAS = Path("tests/fixture/scrape_resp.json").read_text()


@pytest.fixture
def db() -> MetaDatabase:
    return MetaDatabase()


@pytest.fixture
def metas() -> list[PasteMeta]:
    return [PasteMeta(**p) for p in json.loads(METAS)]


@pytest.fixture
def meta(metas: list[PasteMeta]) -> PasteMeta:
    return choice(metas)


def test_init_creates_table(db: MetaDatabase) -> None:
    # Use our own query to confirm table exists.

    with db.cursor() as cursor:
        query = cursor.execute(f"SELECT count(*) from {db.table_name}")
        result = query.fetchone()

    assert result[0] == 0


def test_insert_row(db: MetaDatabase, meta: PasteMeta) -> None:
    initial = db.insert(meta)
    duplicate = db.insert(meta)
    row_count = db.row_count

    assert initial is True
    assert duplicate is False
    assert row_count == 1


def test_insert_many_with_one_failure(db: MetaDatabase, metas: list[PasteMeta]) -> None:
    expected_len = len(metas)
    metas.append(metas[0])  # create a duplicate

    results = db.insert_many(metas)

    assert db.row_count == expected_len
    assert len(results) == 1
    assert results[0] == expected_len  # Last entry is duplicate
