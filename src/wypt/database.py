"""Read/Write actions to the sqlite3 database."""
from __future__ import annotations

from collections.abc import Generator
from collections.abc import Sequence
from contextlib import closing
from contextlib import contextmanager
from sqlite3 import Connection
from sqlite3 import Cursor
from typing import NoReturn

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

    def match_count(self) -> int:
        """Current count of rows on the match table."""
        with closing(self._dbconn.cursor()) as cursor:
            query = cursor.execute("SELECT count(key) FROM match;")
            return query.fetchone()[0]

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
            self._dbconn.commit()

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
            self._dbconn.commit()

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
            self._dbconn.commit()

    def get_match_views(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[model.MatchView]:
        """
        Get a list of match views from the database.

        Args:
            limit: Limit the number of rows to return.
            offset: Determine the offset start of the rows returned

        Returns:
            A list of model.MatchView object. List can be empty.
        """
        sql = """\
            SELECT
                match.key,
                meta.date,
                meta.title,
                meta.full_url,
                match.match_name,
                match.match_value
            FROM
                match
                INNER JOIN meta ON meta.key = match.key
            ORDER BY meta.date
            LIMIT ? OFFSET ?;
        """
        with closing(self._dbconn.cursor()) as cursor:
            cursor.execute(sql, (limit, offset))
            rows = cursor.fetchall()

        return [
            model.MatchView(
                key=row[0],
                date=row[1],
                title=row[2],
                full_url=row[3],
                match_name=row[4],
                match_value=row[5],
            )
            for row in rows
        ]

    def get_keys_to_pull(self, limit: int = 25) -> list[str]:
        """Return keys from meta table that have not been pulled into paste table."""
        sql = """\
            SELECT
                meta.key
            FROM
                meta
                LEFT JOIN paste ON paste.key = meta.key
            WHERE
                paste.key IS NULL
            LIMIT ?;
        """
        with closing(self._dbconn.cursor()) as cursor:
            cursor.execute(sql, (limit,))
            rows = cursor.fetchall()

        return [row[0] for row in rows]

    def _table_guard(self, table: str) -> None | NoReturn:
        """Raise KeyError if table name has not been added to class."""
        if table not in self._tables:
            raise KeyError(f"Invalid table '{table}' provided.")

        return None
