"""Process requetss from API and return results."""
from __future__ import annotations

import logging
from typing import Any

try:
    from typing import Protocol
except ImportError:  # pragma: no cover
    from typing_extensions import Protocol  # type: ignore

from .model import BaseModel


class Database_(Protocol):
    def get(
        self, table: str, next_: str | None, *, limit: int = 100
    ) -> tuple[list[BaseModel], str | None]:
        ...


class APIHandler:
    logger = logging.getLogger()

    def __init__(self, database: Database_) -> None:
        """Initialize API handler."""
        self._database = database

    def get_table_dct(
        self, table: str, next_: str | None, limit: int = 100
    ) -> dict[str, Any]:
        """Get selected table, up to 100 rows, as dictionary."""
        rows, next_ = self._database.get(table, next_, limit=limit)
        return {
            "rows": [row.to_dict() for row in rows],
            "next": next_,
        }
