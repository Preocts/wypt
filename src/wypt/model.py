"""Data models for API responses."""
from __future__ import annotations

import dataclasses
import json

__all__ = ["PasteMeta"]


@dataclasses.dataclass(frozen=True)
class BaseModel:
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

    scrape_url: str
    full_url: str
    date: str
    key: str
    size: str
    expire: str
    title: str
    syntax: str
    user: str
    hits: str


@dataclasses.dataclass(frozen=True)
class Paste(BaseModel):
    """
    Model data from the `paste` table.

    NOTE: Order of attributes is important and should match the respective table.
    """

    key: str
    content: str
