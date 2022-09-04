from __future__ import annotations

import json
from pathlib import Path
from random import choice

import pytest
from wypt.model import Paste
from wypt.paste_database import PasteDatabase


PASTES = Path("tests/fixture/paste.json").read_text()

# NOTE: Tests unique methods to class.
# `Database` super class tested in `meta_database_test.py`


@pytest.fixture
def db() -> PasteDatabase:
    return PasteDatabase()


@pytest.fixture
def pastes() -> list[Paste]:
    return [Paste(**p) for p in json.loads(PASTES)]


@pytest.fixture
def paste(pastes: list[Paste]) -> Paste:
    return choice(pastes)


def test_init_creates_table(db: PasteDatabase) -> None:
    # Use our own query to confirm table exists.

    with db.cursor() as cursor:
        query = cursor.execute(f"SELECT count(*) from {db.table_name}")
        result = query.fetchone()

    assert result[0] == 0


def test_insert_row(db: PasteDatabase, paste: Paste) -> None:
    initial = db.insert(paste)
    duplicate = db.insert(paste)
    row_count = db.row_count

    assert initial is True
    assert duplicate is False
    assert row_count == 1


def test_insert_many_with_one_failure(
    db: PasteDatabase,
    pastes: list[Paste],
) -> None:
    expected_len = len(pastes)
    pastes.append(pastes[0])  # create a duplicate

    results = db.insert_many(pastes)

    assert db.row_count == expected_len
    assert len(results) == 1
    assert results[0] == expected_len  # Last entry is duplicate
