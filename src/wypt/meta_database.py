"""Access Meta table for pastes."""
from __future__ import annotations

from .database import Database


class MetaDatabase(Database):
    """Access Meta table for pastes."""

    def __init__(
        self,
        db_file: str = ":memory:",
        sql_file: str = "tables/meta_database_tbl.sql",
        table_name: str = "pastemeta",
    ) -> None:
        self.sql_file = sql_file
        self.table_name = table_name
        super().__init__(db_file)
