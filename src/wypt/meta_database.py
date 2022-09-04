"""Access Meta table for pastes."""
from __future__ import annotations

from typing import Sequence

from .database import Database
from .model import PasteMeta


class MetaDatabase(Database):
    """Access Meta table for pastes."""

    def __init__(
        self,
        db_file: str = ":memory:",
        sql_file: str = "meta_database_tbl.sql",
        table_name: str = "pastemeta",
    ) -> None:
        self.sql_file = sql_file
        self.table_name = table_name
        super().__init__(db_file)

    def insert(self, paste: PasteMeta) -> bool:
        """Insert paste into table, returns false on failure."""
        return self._insert(paste.to_dict())

    def insert_many(self, pastes: Sequence[PasteMeta]) -> tuple[int, ...]:
        """Insert many pastes into table, returns index of failures if any."""
        return self._insert_many([paste.to_dict() for paste in pastes])
