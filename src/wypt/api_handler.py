"""Process requetss from API and return results."""

from __future__ import annotations

import logging

from .database import Database as _Database
from .model import MatchView


class APIHandler:
    logger = logging.getLogger()

    def __init__(self, database: _Database) -> None:
        """Initialize API handler."""
        self._database = database

    def align_pagination(self, limit: int, offset: int) -> tuple[int, int]:
        """
        Align limit and offset to valid values.

        If limit is less than 1, set to 1.
        If offset is less than 0, set to 0.

        if offset is greater than the number of records, set to the last page.
        """
        limit = limit if limit > 0 else 1
        offset = offset if offset > 0 else 0

        row_count = self._database.match_count()

        if offset > row_count:
            offset = row_count // limit * limit

        if offset == row_count:
            offset = row_count - limit

        return limit, offset

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
        total_pages = total_pages + 1 if row_count % limit else total_pages

        current_page = (offset // limit) + 1

        return str(current_page), str(total_pages)

    def delete_matchview(self, key: str) -> bool:
        """Delete a MatchView record."""
        return self._database.delete_match_view(key)

    @staticmethod
    def _clean_split(text: str, delimiter: str = ",") -> list[str]:
        """Split text on delimeter, strips leading/trailing whitespace."""
        return [seg.strip() for seg in text.split(delimiter)] if text else []
