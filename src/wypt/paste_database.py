"""Access Paste table for pastes."""
from __future__ import annotations

from .database import Database


class PasteDatabase(Database):
    """Access Paste table for pastes."""

    def __init__(
        self,
        db_file: str = ":memory:",
        sql_file: str = "tables/paste_database_tbl.sql",
        table_name: str = "paste",
    ) -> None:
        self.sql_file = sql_file
        self.table_name = table_name
        super().__init__(db_file)
