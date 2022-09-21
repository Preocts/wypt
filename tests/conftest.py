from __future__ import annotations

import json
from pathlib import Path
from sqlite3 import Connection
from typing import List
from typing import Tuple

import pytest
from wypt.database import Database
from wypt.model import BaseModel
from wypt.model import Match
from wypt.model import Meta
from wypt.model import Paste

METAS = Path("tests/fixture/scrape_resp.json").read_text()
PASTES = Path("tests/fixture/paste.json").read_text()
MATCHES = Path("tests/fixture/match.json").read_text()

META_ROWS = [Meta(**d) for d in json.loads(METAS)]
PASTE_ROWS = [Paste(**d) for d in json.loads(PASTES)]
MATCH_ROWS = [Match(**d) for d in json.loads(MATCHES)]

TABLE_DATA = [
    ("meta", META_ROWS),
    ("paste", PASTE_ROWS),
    ("match", MATCH_ROWS),
]
T_Data = Tuple[str, List[BaseModel]]


@pytest.fixture
def db() -> Database:
    dbconn = Connection(":memory:")

    database = Database(dbconn)
    database.add_table("paste", "tables/paste_database_tbl.sql", Paste)
    database.add_table("meta", "tables/meta_database_tbl.sql", Meta)
    database.add_table("match", "tables/match_database_tbl.sql", Match)
    return database


@pytest.fixture
def mock_database(db: Database) -> Database:
    db.insert_many("meta", META_ROWS)
    db.insert_many("paste", PASTE_ROWS)
    db.insert_many("match", MATCH_ROWS)
    return db
