from __future__ import annotations

import json
from pathlib import Path

import pytest
from wypt.model import BaseModel
from wypt.model import Match
from wypt.model import Meta
from wypt.model import Paste


@pytest.mark.parametrize(
    ("fixture", "model"),
    (
        ("tests/fixture/scrape_resp.json", Meta),
        ("tests/fixture/paste.json", Paste),
        ("tests/fixture/match.json", Match),
    ),
)
def test_model_create_and_deconstruct(fixture: str, model: type[BaseModel]) -> None:
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
def test_model_str(model: BaseModel) -> None:
    result = str(model)

    assert len(result) == 79
