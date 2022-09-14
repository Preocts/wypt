"""Read/Write actions to the sqlite3 database."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from sqlite3 import Connection
from sqlite3 import Cursor
from sqlite3 import IntegrityError
from typing import Generator
from typing import Sequence

from .model import BaseModel


class Database:
    def __init__(self, database_connection: Connection) -> None:
        """Read/Write actions to the sqlite3 database."""
        self._dbconn = database_connection
        self._tables: dict[str, type[BaseModel]] = {}

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
        for row in self.get_iter(table):
            print(str(row))

    def row_count(self, table: str) -> int:
        """Current count of rows in database."""
        with self.cursor() as cursor:
            query = cursor.execute(f"SELECT count(*) FROM {table}")
            return query.fetchone()[0]

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

    def insert(self, table: str, row_data: BaseModel) -> bool:
        """Insert paste into table, returns false on failure."""
        # If insert_many returns no failues, insert had success.
        return not (self.insert_many(table, [row_data]))

    def insert_many(self, table: str, rows: Sequence[BaseModel]) -> tuple[int, ...]:
        """Insert many pastes into table, returns index of failures if any."""
        model_dct = rows[0].to_dict()
        columns = ",".join(list(model_dct.keys()))
        values_ph = ",".join(["?" for _ in model_dct.keys()])
        failures: list[int] = []
        for idx, row in enumerate(rows):
            values = list(row.to_dict().values())
            sql = f"INSERT INTO {table} ({columns}) VALUES({values_ph})"

            with self.cursor(commit_on_exit=True) as cursor:
                try:
                    cursor.execute(sql, values)
                except IntegrityError:
                    failures.append(idx)

        return tuple(failures)

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
        last_row_index = 0
        with self.cursor() as cursor:
            while "the grass grows":
                sql = f"SELECT *, rowid FROM {table} WHERE rowid > ? LIMIT ?"

                cursor.execute(sql, (last_row_index, limit))

                rows = cursor.fetchall()

                if not rows:
                    break

                for row in rows:
                    row_lst = list(row)
                    last_row_index = row_lst.pop()
                    yield self._tables[table](*row_lst)

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

        sql = (
            f"SELECT a.key FROM {left_table} a "
            f"LEFT JOIN {right_table} b "
            f"ON a.key = b.key WHERE b.key IS NULL LIMIT ?"
        )

        with self.cursor() as cursor:
            cursor.execute(sql, (limit,))
            results = cursor.fetchall()

        return [r[0] for r in results]
