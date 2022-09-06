"""Access Meta table for pastes."""
from __future__ import annotations

from .database import Database
from .paste_database import PasteDatabase


class MetaDatabase(Database):
    """Access Meta table for pastes."""

    sql_file: str = "tables/meta_database_tbl.sql"
    table_name: str = "pastemeta"

    @property
    def to_gather_count(self) -> int:
        """Return number of rows remaining to gather."""
        sql = (
            f"SELECT count(a.key) FROM {self.table_name} a "
            f"LEFT JOIN {PasteDatabase.table_name} b "
            f"ON a.key = b.key WHERE b.key IS NULL"
        )

        with self.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchone()[0]

    def get_keys_to_fetch(self, limit: int = 25) -> tuple[str, ...]:
        """
        Return `limit` of paste key values that have not been fetched.

        NOTE: Can return less than `limit` or empty results.
        """

        sql = (
            f"SELECT a.key FROM {self.table_name} a "
            f"LEFT JOIN {PasteDatabase.table_name} b "
            f"ON a.key = b.key WHERE b.key IS NULL LIMIT ?"
        )

        with self.cursor() as cursor:
            cursor.execute(sql, (limit,))
            results = cursor.fetchall()

        return tuple(r[0] for r in results)
