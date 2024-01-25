"""Process requetss from API and return results."""
from __future__ import annotations

import logging
from typing import Any

from .database import Database as _Database
from .model import MatchView


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

    def get_matchview(self, limit: int = 100, offset: int = 0) -> list[MatchView]:
        """Get a list of MatchView objects for rendering."""
        return self._database.get_match_views(limit, offset)

    def get_matchview_params(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[str, str]:
        """Get the previous and next params for table pagination."""
        total_rows = self._database.match_count()
        previous_page = ""
        next_page = ""

        if (offset - limit) >= 0:
            previous_page = f"limit={limit}&offset={offset - limit}"

        if (limit + offset) < total_rows:
            next_page = f"limit={limit}&offset={offset + limit}"

        return previous_page, next_page

    def get_matchview_pages(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[str, str]:
        """Get the current page and total pages."""
        row_count = self._database.match_count()
        limit = limit if limit else 1
        total_pages = row_count // limit
        current_page = (offset // limit) + 1
        print(f"{total_pages=}, {current_page=}")

        return str(current_page), str(total_pages)

    def delete_table_rows(self, table: str, keys: str) -> dict[str, Any]:
        """Delete selected rows from table. Always returns empty response. (204)"""
        key_lst = self._clean_split(keys)
        self._database.delete_many(table, key_lst)
        return {}

    @staticmethod
    def _clean_split(text: str, delimiter: str = ",") -> list[str]:
        """Split text on delimeter, strips leading/trailing whitespace."""
        return [seg.strip() for seg in text.split(delimiter)] if text else []
