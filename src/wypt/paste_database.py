"""Access Paste table for pastes."""
from __future__ import annotations

from .database import Database
from .model import Paste


class PasteDatabase(Database):
    """Access Paste table for pastes."""

    sql_file = "tables/paste_database_tbl.sql"
    table_name = "paste"
    model = Paste
