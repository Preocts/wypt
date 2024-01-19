"""Process requetss from API and return results."""
from __future__ import annotations

import logging
from typing import Any

from .database import Database as _Database


class APIHandler:
    logger = logging.getLogger()

    def __init__(self, database: _Database) -> None:
        """Initialize API handler."""
        self._database = database

    def get_table_dct(
        self,
        table: str,
        next_: str | None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Get selected table, up to 100 rows, as dictionary."""
        rows, next_ = self._database.get(table, next_, limit=limit)
        return {
            "rows": [row.to_dict() for row in rows],
            "next": next_,
        }

    def delete_table_rows(self, table: str, keys: str) -> dict[str, Any]:
        """Delete selected rows from table. Always returns empty response. (204)"""
        key_lst = self._clean_split(keys)
        self._database.delete_many(table, key_lst)
        return {}

    @staticmethod
    def _clean_split(text: str, delimiter: str = ",") -> list[str]:
        """Split text on delimeter, strips leading/trailing whitespace."""
        return [seg.strip() for seg in text.split(delimiter)] if text else []
