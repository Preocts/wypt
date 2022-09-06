"""Access Meta table for pastes."""
from __future__ import annotations

from .database import Database


class MetaDatabase(Database):
    """Access Meta table for pastes."""

    sql_file: str = "tables/meta_database_tbl.sql"
    table_name: str = "pastemeta"
