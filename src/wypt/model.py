"""Data models for API responses."""
from __future__ import annotations

import dataclasses
import json
from datetime import datetime

__all__ = ["BaseModel", "PasteMeta", "Paste", "Match"]


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


@dataclasses.dataclass(frozen=True)
class PasteMeta(BaseModel):
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
        return f"{self.full_url:21} | {dt:19} | {self.title[:25]:25} | {self.syntax:12}"


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
        return f"{url + self.key:21} | {self.content[:50]:50}"


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
