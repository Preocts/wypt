"""Store meta data of pastes."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from pathlib import Path
from sqlite3 import Connection
from sqlite3 import Cursor
from typing import Generator


class MetaDatabase:

    logger = logging.getLogger(__name__)
    sql_file = "meta_database_tbl.sql"

    def __init__(self, db_file: str = ":memory:") -> None:
        """Provide target file for database. Default uses memory."""
        self._dbconn = Connection(db_file)
        self.logger.debug("Opened database connection to %s", db_file)

        self._create_table()

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
