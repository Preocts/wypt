"""Runtime setup actions and config loading."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from sqlite3 import Connection
from typing import Any

import tomli

from .database import Database
from .model import Match
from .model import Meta
from .model import Paste


@dataclass(frozen=True)
class _Config:
    logging_level: str = "WARNING"
    logging_format: str = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    database_file: str = "wypt_database.sqlite3"
    pattern_file: str = "wypt.toml"
    retain_posts_for_days: int = 1


class Runtime:
    """Runtime setup actions and config loading."""

    def __init__(self) -> None:
        """Provide runtime setup utility."""
        self._config: _Config | None = None
        self._database: Database | None = None

    def get_config(self) -> _Config:
        """Return loaded config, will load default if not already loaded."""
        if self._config is None:
            self._config = self.load_config()
        return self._config

    def get_database(self) -> Database:
        """Return connected database, will connect in-memory if not connected."""
        if self._database is None:
            self._database = self.connect_database()
        return self._database

    def connect_database(self, database_file: str = ":memory:") -> Database:
        """Connect to sqlite3 database. Uses in-memory location by default."""
        if self._database is None:
            # Connect to and build database
            dbconn = Connection(self.get_config().database_file)
            self._database = Database(dbconn)
            self._database.add_table("paste", "tables/paste_database_tbl.sql", Paste)
            self._database.add_table("meta", "tables/meta_database_tbl.sql", Meta)
            self._database.add_table("match", "tables/match_database_tbl.sql", Match)
        return self._database

    def load_config(self, config_file: str = "wypt.toml") -> _Config:
        """Load and return config file. Uses defaults if not found."""
        _config_file = Path(config_file)
        config: dict[str, Any] = {}
        if _config_file.exists():
            config = tomli.load(_config_file.open("rb")).get("CONFIG") or {}
        self._config = _Config(**config) if config else _Config()
        return self._config

    def set_logging(self) -> None:
        """Set root logging with defined format."""
        # Purposely use basicConfig to avoid mucking with loggers already set.
        logging.basicConfig(
            level=self.get_config().logging_level,
            format=self.get_config().logging_format,
        )
