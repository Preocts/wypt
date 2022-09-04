"""Superclass to database classes."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from sqlite3 import Connection
from sqlite3 import Cursor
from sqlite3 import IntegrityError
from typing import Any
from typing import Generator
from typing import Sequence


class Database:

    sql_file: str
    table_name: str

    def __init__(self, db_file: str = ":memory:") -> None:
        """Provide target file for database. Default uses memory."""
        self._dbconn = Connection(db_file)

        self._create_table()

    @property
    def row_count(self) -> int:
        """Current count of rows in database."""
        with self.cursor() as cursor:
            query = cursor.execute(f"SELECT count(*) FROM {self.table_name}")
            return query.fetchone()[0]

    def _create_table(self) -> None:
        """Create table in database if it does not exist."""
        sql = Path(Path(__file__).parent / self.sql_file).read_text()

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

    def _insert(self, row_data: dict[str, Any]) -> bool:
        """Insert paste into table, returns false on failure."""
        # If insert_many returns no failues, insert had success.
        return not (self._insert_many([row_data]))

    def _insert_many(self, rows: Sequence[dict[str, Any]]) -> tuple[int, ...]:
        """Insert many pastes into table, returns index of failures if any."""
        columns = ",".join(list(rows[0].keys()))
        values_ph = ",".join(["?" for _ in rows[0].keys()])
        failures: list[int] = []

        for idx, row in enumerate(rows):

            values = list(row.values())
            sql = f"INSERT INTO {self.table_name} ({columns}) VALUES({values_ph})"

            with self.cursor(commit_on_exit=True) as cursor:
                try:
                    cursor.execute(sql, values)
                except IntegrityError:
                    failures.append(idx)

        return tuple(failures)