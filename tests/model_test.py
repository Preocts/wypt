from __future__ import annotations

import json
from pathlib import Path

import pytest
from wypt.model import BaseModel
from wypt.model import PasteMeta


@pytest.mark.parametrize(
    ("fixture", "model"), (("tests/fixture/scrape_resp.json", PasteMeta),)
)
def test_model_create_and_deconstruct(fixture: str, model: BaseModel) -> None:
    resps = json.loads(Path(fixture).read_text())

    for resp in resps:
        expected_json = json.dumps(resp, sort_keys=True)
        test_model = model(**resp)  # type: ignore

        test_dict = test_model.to_dict()
        test_json = test_model.to_json()

        assert test_dict == resp
        assert test_json == expected_json
