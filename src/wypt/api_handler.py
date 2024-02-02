"""Process requetss from API and return results."""

from __future__ import annotations

import logging

from .database import Database as _Database
from .model import MatchViewContext


class APIHandler:
    logger = logging.getLogger()

    def __init__(self, database: _Database) -> None:
        """Initialize API handler."""
        self._database = database

    def get_matchview_context(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> MatchViewContext:
        """Get a MatchViewContext object for rendering."""
        row_count = self._database.match_count()

        # Align pagination to valid values to prevent offset overflow on row delete
        if offset > row_count:
            offset = row_count // limit * limit

            if offset == row_count:
                offset = row_count - limit

        total_pages = row_count // limit
        total_pages = total_pages + 1 if row_count % limit else total_pages
        current_page = (offset // limit) + 1

        return MatchViewContext(
            limit=limit,
            offset=offset,
            current_page=current_page,
            total_pages=total_pages,
            total_rows=row_count,
            matchviews=self._database.get_match_views(limit, offset),
        )

    def delete_matchview(self, key: str) -> bool:
        """Delete a MatchView record."""
        return self._database.delete_match_view(key)

    @staticmethod
    def _clean_split(text: str, delimiter: str = ",") -> list[str]:
        """Split text on delimeter, strips leading/trailing whitespace."""
        return [seg.strip() for seg in text.split(delimiter)] if text else []
