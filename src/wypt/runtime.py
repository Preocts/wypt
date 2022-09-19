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
from .pattern_config import PatternConfig


@dataclass(frozen=True)
class _Config:
    logging_level: str = "WARNING"
    logging_format: str = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    database_file: str = "wypt_database.sqlite3"
    pattern_file: str = "wypt.toml"
    retain_posts_for_days: int = 1


class Runtime:
    """Runtime setup actions and config loading."""

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        """Provide runtime setup utility."""
        self._config: _Config | None = None
        self._database: Database | None = None
        self._patterns: PatternConfig | None = None

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

    def get_patterns(self) -> PatternConfig:
        """Return loaded pattern config, will load default location in not loaded."""
        if self._patterns is None:
            self._patterns = self.load_patterns()
        return self._patterns

    def connect_database(self, database_file: str = ":memory:") -> Database:
        """Connect to sqlite3 database. Uses in-memory location by default."""
        # Connect to and build database
        dbconn = Connection(database_file)
        self._database = Database(dbconn)
        self._database.add_table("paste", "tables/paste_database_tbl.sql", Paste)
        self._database.add_table("meta", "tables/meta_database_tbl.sql", Meta)
        self._database.add_table("match", "tables/match_database_tbl.sql", Match)
        return self._database

    def load_config(self, config_file: str = "wypt.toml") -> _Config:
        """Load and return config file. Uses defaults if not found."""
        config = self._load_toml_section(config_file, "CONFIG")
        self._config = _Config(**config) if config else _Config()
        return self._config

    def load_patterns(self, pattern_file: str = "wypt.toml") -> PatternConfig:
        """Load and return pattern config."""
        patterns = self._load_toml_section(pattern_file, "PATTERNS")
        self._patterns = PatternConfig(patterns)
        return self._patterns

    def set_logging(self) -> None:
        """Set root logging with defined format."""
        # Purposely use basicConfig to avoid mucking with loggers already set.
        logging.basicConfig(
            level=self.get_config().logging_level,
            format=self.get_config().logging_format,
        )

    def _load_toml_section(self, file_name: str, section: str) -> dict[str, Any]:
        """Load toml, handle errors, return specific section or empty dict."""
        try:
            return tomli.load(Path(file_name).open("rb"))[section]

        except KeyError:
            self.logger.error("[%s] section missing from %s", section, file_name)

        except FileNotFoundError:
            self.logger.error("Config file not found: '%s'", file_name)

        except tomli.TOMLDecodeError as err:
            self.logger.error("Invalid toml format in %s - '%s'", file_name, err)

        return {}
