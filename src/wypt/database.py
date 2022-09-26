"""Read/Write actions to the sqlite3 database."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from sqlite3 import Connection
from sqlite3 import Cursor
from typing import Generator
from typing import NoReturn
from typing import Sequence
from uuid import uuid4

from .model import BaseModel


class Database:
    def __init__(self, database_connection: Connection) -> None:
        """Read/Write actions to the sqlite3 database."""
        self._dbconn = database_connection
        self._tables: dict[str, type[BaseModel]] = {}
        self._nexts: dict[str, int] = {}

    def add_table(self, table: str, sql_file: str, model: type[BaseModel]) -> None:
        """
        Create/Add a table from sql_file and model.

        Note: sql_file script is executed on add.

        Args:
            table: Name of the table
            sql_file: SQLite3 script to create table. Should assert IF NOT EXISTS
            model: BaseModel subclass to hold table data
        """
        self._tables[table] = model
        self._create_table(sql_file)

    def to_stdout(self, table: str) -> None:
        """Print table to stdout, renders table model's __str__."""
        self._table_guard(table)
        for row in self.get_iter(table):
            print(str(row))

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

    def _create_table(self, sql_file: str) -> None:
        """Create table in database if it does not exist."""
        sql = Path(Path(__file__).parent / sql_file).read_text()

        with self.cursor(commit_on_exit=True) as cursor:
            cursor.executescript(sql)

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

    def insert(self, table: str, row_data: BaseModel) -> None:
        """Insert paste into table, returns false on failure."""
        # If insert_many returns no failues, insert had success.
        self.insert_many(table, [row_data])

    def insert_many(self, table: str, rows: Sequence[BaseModel]) -> None:
        """Insert many pastes into table, returns index of failures if any."""
        self._table_guard(table)
        model_dct = rows[0].to_dict()
        columns = ",".join(list(model_dct.keys()))
        values_ph = ",".join(["?" for _ in model_dct.keys()])

        values = [list(row.to_dict().values()) for row in rows]
        print(values)

        sql = f"INSERT OR IGNORE INTO {table} ({columns}) VALUES({values_ph})"

        with self.cursor(commit_on_exit=True) as cursor:
            cursor.executemany(sql, values)

    def get(
        self,
        table: str,
        next_: str | None = None,
        *,
        limit: int = 100,
    ) -> tuple[list[BaseModel], str | None]:
        """
        Get rows starting at idx stored next counter or 0 if not provided.

        `next_` is expected to be a UUID used as a lookup for return next
        values in database.

        Returns:
            list[BaseModel],
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

        results: list[BaseModel] = []
        for row in rows:
            row_lst = list(row)
            last_row = row_lst.pop()
            results.append(self._tables[table](*row_lst))

        if last_row < self.max_id(table):
            next_uuid = str(uuid4())
            self._nexts[next_uuid] = last_row

        return results, next_uuid

    def get_iter(
        self,
        table: str,
        *,
        limit: int = 100,
    ) -> Generator[BaseModel, None, None]:
        """
        Get all rows from database via iterator.

        Use the keyword arg `limit` to control the maximum number of rows
        fetched from database at a time. The lower the number the lower
        memory overhead with a tradeoff of more frequent disk I/O.
        """
        self._table_guard(table)
        next_: str | None = "startloop"
        while next_:
            rows, next_ = self.get(table, next_, limit=limit)

            yield from rows

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
