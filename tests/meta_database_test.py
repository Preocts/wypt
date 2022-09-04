from __future__ import annotations

import json
from pathlib import Path
from random import choice

import pytest
from wypt.meta_database import MetaDatabase
from wypt.model import Paste


PASTES = Path("tests/fixture/scrape_resp.json").read_text()


@pytest.fixture
def db() -> MetaDatabase:
    return MetaDatabase()


@pytest.fixture
def pastes() -> list[Paste]:
    return [Paste(**p) for p in json.loads(PASTES)]


@pytest.fixture
def paste(pastes: list[Paste]) -> Paste:
    return choice(pastes)


def test_init_creates_table(db: MetaDatabase) -> None:
    # Use our own query to confirm table exists.

    with db.cursor() as cursor:
        query = cursor.execute("SELECT count(*) from pastemeta")
        result = query.fetchone()

    assert result[0] == 0


def test_insert_row(db: MetaDatabase, paste: Paste) -> None:
    initial = db.insert(paste)
    duplicate = db.insert(paste)
    row_count = db.row_count

    assert initial is True
    assert duplicate is False
    assert row_count == 1


def test_insert_many_with_one_failure(db: MetaDatabase, pastes: list[Paste]) -> None:
    pastes.append(pastes[0])  # create a duplicate

    results = db.insert_many(pastes)

    assert db.row_count == len(pastes) - 1
    assert len(results) == 1
    assert results[0] == len(pastes) - 1  # Last entry is duplicate
