"""Superclass to database classes."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from sqlite3 import Connection
from sqlite3 import Cursor
from sqlite3 import IntegrityError
from typing import Generator
from typing import Sequence

from .model import BaseModel
from .model import Match
from .model import Paste
from .model import PasteMeta


class Database:

    sql_file: str
    table_name: str
    model: type[BaseModel]

    def __init__(self, database_connection: Connection) -> None:
        """Provide target file for database. Default uses memory."""
        self._dbconn = database_connection

        self._create_table()

    def to_stdout(self) -> None:
        """Print table to stdout, renders table model's __str__."""
        for row in self.get_iter():
            print(str(row))

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

    def contains(self, key: str) -> bool:
        """True if database contains given key."""
        sql = f"SELECT count(*) FROM {self.table_name} WHERE key=?"
        with self.cursor() as cursor:
            cursor.execute(sql, (key,))
            result = cursor.fetchone()
        return bool(result[0])

    def insert(self, row_data: BaseModel) -> bool:
        """Insert paste into table, returns false on failure."""
        # If insert_many returns no failues, insert had success.
        return not (self.insert_many([row_data]))

    def insert_many(self, rows: Sequence[BaseModel]) -> tuple[int, ...]:
        """Insert many pastes into table, returns index of failures if any."""
        model_dct = rows[0].to_dict()
        columns = ",".join(list(model_dct.keys()))
        values_ph = ",".join(["?" for _ in model_dct.keys()])
        failures: list[int] = []

        for idx, row in enumerate(rows):

            values = list(row.to_dict().values())
            sql = f"INSERT INTO {self.table_name} ({columns}) VALUES({values_ph})"

            with self.cursor(commit_on_exit=True) as cursor:
                try:
                    cursor.execute(sql, values)
                except IntegrityError:
                    failures.append(idx)

        return tuple(failures)

    def get_iter(self, *, limit: int = 100) -> Generator[BaseModel, None, None]:
        """
        Get all rows from database via iterator.

        Use the keyword arg `limit` to control the maximum number of rows
        fetched from database at a time. The lower the number the lower
        memory overhead with a tradeoff of more frequent disk I/O.
        """
        last_row_index = 0
        with self.cursor() as cursor:
            while "the grass grows":
                sql = f"SELECT *, rowid FROM {self.table_name} WHERE rowid > ? LIMIT ?"

                cursor.execute(sql, (last_row_index, limit))

                rows = cursor.fetchall()

                if not rows:
                    break

                for row in rows:
                    row_lst = list(row)
                    last_row_index = row_lst.pop()
                    yield self.model(*row_lst)


class PasteDatabase(Database):
    """Access Paste table for pastes."""

    sql_file = "tables/paste_database_tbl.sql"
    table_name = "paste"
    model = Paste


class MetaDatabase(Database):
    """Access Meta table for pastes."""

    sql_file: str = "tables/meta_database_tbl.sql"
    table_name: str = "pastemeta"
    model = PasteMeta

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

    def get_keys_to_fetch(self, limit: int = 25) -> list[str]:
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

        return [r[0] for r in results]


class MatchDatabase(Database):
    """Access Paste table for pastes."""

    sql_file = "tables/match_database_tbl.sql"
    table_name = "match"
    model = Match
