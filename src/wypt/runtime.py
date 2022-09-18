"""Runtime setup actions and config loading."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomli


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

    @property
    def config(self) -> _Config:
        """Return loaded config, will load default if not already loaded."""
        if self._config is None:
            self._config = self.load_config()
        return self._config

    def load_config(self, config_file: str = "wypt.toml") -> _Config:
        """Load config and set logging. Uses defaults if not found."""
        _config_file = Path(config_file)
        config: dict[str, Any] = {}
        if _config_file.exists():
            config = tomli.load(_config_file.open("rb")).get("CONFIG") or {}
        return _Config(**config) if config else _Config()

    def set_logging(self) -> None:
        """Set root logging with defined format."""
        # Purposely use basicConfig to avoid mucking with loggers already set.
        logging.basicConfig(
            level=self.config.logging_level,
            format=self.config.logging_format,
        )
