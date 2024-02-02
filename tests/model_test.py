from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from wypt.model import Match
from wypt.model import Meta
from wypt.model import Paste
from wypt.model import Serializable


@pytest.mark.parametrize(
    ("fixture", "model"),
    (
        ("tests/fixture/scrape_resp.json", Meta),
        ("tests/fixture/paste.json", Paste),
        ("tests/fixture/match.json", Match),
    ),
)
def test_model_create_and_deconstruct(fixture: str, model: type[Serializable]) -> None:
    resps = json.loads(Path(fixture).read_text())

    for resp in resps:
        expected_json = json.dumps(resp, sort_keys=True)
        test_model = model(**resp)

        test_dict = test_model.to_dict()
        test_json = test_model.to_json()

        assert test_dict == resp
        assert test_json == expected_json


@pytest.mark.parametrize(
    "model",
    (
        Match("test", "test", "test"),
        Paste("test", "test"),
        Meta("tst", "tst", "tst", "0", "0", "0", "tst", "tst", "tst", "0"),
    ),
)
def test_model_str(model: Serializable) -> None:
    result = str(model)

    # TODO: LOL? Why are all the __str__ attributes required to be 79 characters?
    assert len(result) == 79


def test_validate_meta_model_sql() -> None:
    db = sqlite3.connect(":memory:")
    cursor = db.cursor()

    cursor.executescript(Meta.as_sql())

    db.commit()
    db.close()


def test_validate_match_model_sql() -> None:
    db = sqlite3.connect(":memory:")
    cursor = db.cursor()

    cursor.executescript(Match.as_sql())

    db.commit()
    db.close()


def test_validate_paste_model_sql() -> None:
    db = sqlite3.connect(":memory:")
    cursor = db.cursor()

    cursor.executescript(Paste.as_sql())

    db.commit()
    db.close()
