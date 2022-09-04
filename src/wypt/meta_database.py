"""Store meta data of pastes."""
from __future__ import annotations

from sqlite3 import IntegrityError
from typing import Sequence

from .database import Database
from .model import Paste


class MetaDatabase(Database):

    sql_file = "meta_database_tbl.sql"
    table_name = "pastemeta"

    def insert(self, paste: Paste) -> bool:
        """Insert paste into table, returns false on failure."""
        # If insert_many returns no failues, insert had success.
        return not (self.insert_many([paste]))

    def insert_many(self, pastes: Sequence[Paste]) -> tuple[int, ...]:
        """Insert many pastes into table, returns index of failures if any."""
        paste_dict = pastes[0].to_dict()
        columns = ",".join(list(paste_dict.keys()))
        values_ph = ",".join(["?" for _ in paste_dict.keys()])
        failures: list[int] = []

        for idx, paste in enumerate(pastes):

            values = list(paste.to_dict().values())
            sql = f"INSERT INTO {self.table_name} ({columns}) VALUES({values_ph})"

            with self.cursor(commit_on_exit=True) as cursor:
                try:
                    cursor.execute(sql, values)
                except IntegrityError:
                    self.logger.warning("Integrity Error, '%s' exists.", paste.key)
                    failures.append(idx)

        return tuple(failures)
