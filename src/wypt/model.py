"""Data models for API responses."""

from __future__ import annotations

import dataclasses
import json
from datetime import datetime

__all__ = ["BaseModel", "Meta", "Paste", "Match"]


@dataclasses.dataclass(frozen=True)
class BaseModel:
    """Base model for all data models."""

    key: str

    def to_dict(self) -> dict[str, str]:
        """Convert model to a dictionary."""
        return dataclasses.asdict(self)

    def to_json(self) -> str:
        """Convert model to JSON serialized string."""
        return json.dumps(self.to_dict(), sort_keys=True)

    @staticmethod
    def as_sql() -> str:
        """Render model as sql table creation string."""
        raise NotImplementedError()


@dataclasses.dataclass(frozen=True)
class Meta(BaseModel):
    """
    Model data from the `pastemeta` table.

    NOTE: Order of attributes is important and should match the respective table.
    """

    key: str
    scrape_url: str
    full_url: str
    date: str
    size: str
    expire: str
    title: str
    syntax: str
    user: str
    hits: str

    def __str__(self) -> str:
        dt = str(datetime.fromtimestamp(float(self.date)))
        return f"{self.full_url:21} | {dt:19} | {self.title[:18]:18} | {self.syntax:12}"

    @staticmethod
    def as_sql() -> str:
        """Render model as sql table creation string."""
        return """\
-- Order of table columns much match the `Meta` dataclass model.
CREATE TABLE IF NOT EXISTS meta (
    key text NOT NULL,
    scrape_url text NOT NULL,
    full_url text NOT NULL,
    date text NOT NULL,
    size text NOT NULL,
    expire text NOT NULL,
    title text NOT NULL,
    syntax text NOT NULL,
    user text NOT NULL,
    hits text NOT NULL
);

-- Create a unique index on the paste_key
CREATE UNIQUE INDEX IF NOT EXISTS meta_key ON meta(key);
-- Create an index on the syntax flag for searching
CREATE INDEX IF NOT EXISTS syntax_flag ON meta(syntax);
"""


@dataclasses.dataclass(frozen=True)
class Paste(BaseModel):
    """
    Model data from the `paste` table.

    NOTE: Order of attributes is important and should match the respective table.
    """

    key: str
    content: str

    def __str__(self) -> str:
        url = "https://pastebin.com/"
        return f"{url + self.key:21} | {self.content[:51]:51}"

    @staticmethod
    def as_sql() -> str:
        """Render model as sql table creation string."""
        return """\
-- Order of table columns much match the `Paste` dataclass model.
CREATE TABLE IF NOT EXISTS paste (
    key text NOT NULL,
    content text NOT NULL
);

-- Create a unique index on the paste key
CREATE UNIQUE INDEX IF NOT EXISTS paste_key ON paste(key);
"""


@dataclasses.dataclass(frozen=True)
class Match(BaseModel):
    """
    Model data from the `paste` table.

    NOTE: Order of attributes is important and should match the respective table.
    """

    key: str
    match_name: str
    match_value: str

    def __str__(self) -> str:
        return f"{self.key:8} | {self.match_name[:15]:15} | {self.match_value[:50]:50}"

    @staticmethod
    def as_sql() -> str:
        """Render model as sql table creation string."""
        return """\
-- Order of table columns much match the `Match` dataclass model.
CREATE TABLE IF NOT EXISTS match (
    key text NOT NULL,
    match_name text NOT NULL,
    match_value text NOT NULL
);

-- Create a unique index on the paste key
CREATE UNIQUE INDEX IF NOT EXISTS match_key ON match(key, match_name, match_value);
"""


@dataclasses.dataclass(frozen=True)
class MatchView:
    """A view of a match used by the web front-end to render results."""

    key: str
    date: str
    title: str
    full_url: str
    match_name: str
    match_value: str
