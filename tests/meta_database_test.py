from __future__ import annotations

import json
from pathlib import Path
from sqlite3 import Connection

from wypt.meta_database import MetaDatabase
from wypt.model import Paste
from wypt.model import PasteMeta
from wypt.paste_database import PasteDatabase


METAS = Path("tests/fixture/scrape_resp.json").read_text()


def test_get_keys_to_fetch() -> None:
    # Overly complex setup joyness
    # Setup two databases with mock data. Results should expect
    # all keys of meta fixture to be returns sans 0th index key.
    conn = Connection(":memory:")
    pastedb = PasteDatabase(conn)
    metadb = MetaDatabase(conn)
    metas = [PasteMeta(**meta) for meta in json.loads(METAS)]
    paste = Paste(metas[0].key, "", "")
    metadb.insert_many(metas)
    pastedb.insert(paste)

    results = metadb.get_keys_to_fetch()
    print(results)

    assert metas[0].key not in results
    assert len(results) == len(metas) - 1
