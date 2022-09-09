"""Access Paste table for pastes."""
from __future__ import annotations

from .database import Database
from .model import Match


class MatchDatabase(Database):
    """Access Paste table for pastes."""

    sql_file = "tables/match_database_tbl.sql"
    table_name = "match"
    model = Match

    def to_stdout(self) -> None:
        """Print table out."""
        for row in self.get_iter():
            print(str(row))
