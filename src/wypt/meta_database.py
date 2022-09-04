"""Store meta data of pastes."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from pathlib import Path
from sqlite3 import Connection
from sqlite3 import Cursor
from sqlite3 import IntegrityError
from typing import Generator
from typing import Sequence

from .model import Paste


class MetaDatabase:

    logger = logging.getLogger(__name__)
    sql_file = "meta_database_tbl.sql"

    def __init__(self, db_file: str = ":memory:") -> None:
        """Provide target file for database. Default uses memory."""
        self._dbconn = Connection(db_file)
        self.logger.debug("Opened database connection to %s", db_file)

        self._create_table()

    @property
    def row_count(self) -> int:
        """Current count of rows in database."""
        with self.cursor() as cursor:
            query = cursor.execute("SELECT count(*) FROM pastemeta")
            return query.fetchone()[0]

    def _create_table(self) -> None:
        """Create table in database if it does not exist."""
        # cwd = Path(__file__).parent
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

    def insert(self, paste: Paste) -> bool:
        """Insert paste into table, returns false on failure."""
        paste_dict = paste.to_dict()
        columns = ",".join(list(paste_dict.keys()))
        values_ph = ",".join(["?" for _ in paste_dict.keys()])

        sql = f"INSERT INTO pastemeta ({columns}) VALUES({values_ph})"
        values = list(paste_dict.values())

        with self.cursor(commit_on_exit=True) as cursor:
            try:
                cursor.execute(sql, values)
            except IntegrityError:
                self.logger.warning("Integrity Error, '%s' exists.", paste.key)
                return False
        return True

    def insert_many(self, pastes: Sequence[Paste]) -> tuple[int, ...]:
        """Insert many pastes into table, returns index of failures if any."""
        paste_dict = pastes[0].to_dict()
        columns = ",".join(list(paste_dict.keys()))
        values_ph = ",".join(["?" for _ in paste_dict.keys()])
        failures: list[int] = []

        for idx, paste in enumerate(pastes):

            values = list(paste.to_dict().values())
            sql = f"INSERT INTO pastemeta ({columns}) VALUES({values_ph})"

            with self.cursor(commit_on_exit=True) as cursor:
                try:
                    cursor.execute(sql, values)
                except IntegrityError:
                    self.logger.warning("Integrity Error, '%s' exists.", paste.key)
                    failures.append(idx)

        return tuple(failures)
