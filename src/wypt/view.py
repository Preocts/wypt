from __future__ import annotations

from sqlite3 import Connection

from .database import MatchDatabase

if __name__ == "__main__":
    dbconn = Connection("wypt_db.sqlite3")

    db = MatchDatabase(dbconn)
    db.to_stdout()
