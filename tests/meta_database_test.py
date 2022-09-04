from __future__ import annotations

import pytest
from wypt.meta_database import MetaDatabase


@pytest.fixture
def db() -> MetaDatabase:
    return MetaDatabase()


def test_init_creates_table(db: MetaDatabase) -> None:
    # Use our own query to confirm table exists.

    with db.cursor() as cursor:
        query = cursor.execute("SELECT count(*) from pastemeta")
        result = query.fetchone()

    assert result[0] == 0
