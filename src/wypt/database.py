"""Read/Write actions to the sqlite3 database."""
from __future__ import annotations

from collections.abc import Generator
from collections.abc import Sequence
from contextlib import closing
from contextlib import contextmanager
from sqlite3 import Connection
from sqlite3 import Cursor
from typing import NoReturn
from uuid import uuid4

from wypt import model


class Database:
    def __init__(self, database_connection: Connection) -> None:
        """Read/Write actions to the sqlite3 database."""
        self._dbconn = database_connection
        self._tables: dict[str, type[model.BaseModel]] = {}
        self._nexts: dict[str, int] = {}

    def init_tables(self) -> None:
        """Create/Add defined tables to the database."""
        self._tables["paste"] = model.Paste
        self._tables["meta"] = model.Meta
        self._tables["match"] = model.Match

        with self.cursor(commit_on_exit=True) as cursor:
            cursor.executescript(model.Paste.as_sql())
            cursor.executescript(model.Meta.as_sql())
            cursor.executescript(model.Match.as_sql())

    def row_count(self, table: str) -> int:
        """Current count of rows in table."""
        self._table_guard(table)
        with self.cursor() as cursor:
            query = cursor.execute(f"SELECT count(*) FROM {table}")
            return query.fetchone()[0]

    def max_id(self, table: str) -> int:
        """Current max row_id in table."""
        self._table_guard(table)
        with self.cursor() as cursor:
            query = cursor.execute(f"SELECT max(rowid) FROM {table}")
            return query.fetchone()[0] or 0

    @contextmanager
    def cursor(self, *, commit_on_exit: bool = False) -> Generator[Cursor, None, None]:
        """Context manager for cursor creation and cleanup."""
        try:
            cursor = self._dbconn.cursor()
            yield cursor

        finally:
            if commit_on_exit:
                self._dbconn.commit()
            cursor.close()

    def insert_metas(self, metas: Sequence[model.Meta]) -> None:
        """Insert Meta rows in batch. Primary key conflicts are ignored."""
        sql = """\
                INSERT OR IGNORE INTO meta (
                    key,
                    scrape_url,
                    full_url,
                    date,
                    size,
                    expire,
                    title,
                    syntax,
                    user,
                    hits
                ) VALUES (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
"""
        values = [list(meta.to_dict().values()) for meta in metas]

        with closing(self._dbconn.cursor()) as cursor:
            cursor.executemany(sql, values)

    def insert_paste(self, paste: model.Paste) -> None:
        """Insert row into paste table. Constraint violations are ignored."""
        sql = """\
                INSERT OR IGNORE INTO paste (
                    key,
                    content
                ) VALUES (
                    ?,
                    ?
                )
"""
        values = [paste.key, paste.content]

        with closing(self._dbconn.cursor()) as cursor:
            cursor.execute(sql, values)

    def insert_matches(self, matches: Sequence[model.Match]) -> None:
        """Insert Match rows in batch. Primary key conflicts are ignored."""
        sql = """\
                INSERT OR IGNORE INTO match (
                    key,
                    match_name,
                    match_value
                ) VALUES (
                    ?,
                    ?,
                    ?
                )
"""
        values = [list(match.to_dict().values()) for match in matches]

        with closing(self._dbconn.cursor()) as cursor:
            cursor.executemany(sql, values)

    def get(
        self,
        table: str,
        next_: str | None = None,
        *,
        limit: int = 100,
    ) -> tuple[list[model.BaseModel], str | None]:
        """
        Get rows starting at idx stored next counter or 0 if not provided.

        `next_` is expected to be a UUID used as a lookup for return next
        values in database.

        Returns:
            list[model.BaseModel],
            string UUID or None if there are more results to pull
        """
        self._table_guard(table)
        last_row = self._nexts.get(next_, 0) if next_ else 0
        next_uuid: str | None = None
        self._nexts.pop(next_ or "", None)

        sql = f"SELECT *, rowid FROM {table} WHERE rowid > ? LIMIT ?"

        with self.cursor() as cursor:
            cursor.execute(sql, (last_row, limit))

            rows = cursor.fetchall()

        results: list[model.BaseModel] = []
        for row in rows:
            row_lst = list(row)
            last_row = row_lst.pop()
            results.append(self._tables[table](*row_lst))

        if last_row < self.max_id(table):
            next_uuid = str(uuid4())
            self._nexts[next_uuid] = last_row

        return results, next_uuid

    def get_difference(
        self,
        left_table: str,
        right_table: str,
        limit: int = 25,
    ) -> list[str]:
        """
        Return the difference of `key` values on left table against right table.

        NOTE: Can return less than `limit` or empty results.

        Args:
            left_table: Base table for query (has the values to find)
            right_table: table to join and compare against (missing values to find)
        """
        self._table_guard(left_table)
        self._table_guard(right_table)

        sql = (
            f"SELECT a.key FROM {left_table} a "
            f"LEFT JOIN {right_table} b "
            f"ON a.key = b.key WHERE b.key IS NULL LIMIT ?"
        )

        with self.cursor() as cursor:
            cursor.execute(sql, (limit,))
            results = cursor.fetchall()

        return [r[0] for r in results]

    def delete(self, table: str, key: str) -> None:
        """
        Delete a row from the given table by their key.

        Args:
            table: Name of the table
            key: list of keys to delete
        """
        self.delete_many(table, [key])

    def delete_many(self, table: str, keys: list[str]) -> None:
        """
        Delete a list of rows from the given table by their key.

        Args:
            table: Name of the table
            key: list of keys to delete
        """
        self._table_guard(table)

        sql = f"DELETE FROM {table} WHERE key=?"
        values = [[key] for key in keys]

        with self.cursor(commit_on_exit=True) as cursor:
            cursor.executemany(sql, values)

    def _table_guard(self, table: str) -> None | NoReturn:
        """Raise KeyError if table name has not been added to class."""
        if table not in self._tables:
            raise KeyError(f"Invalid table '{table}' provided.")

        return None
