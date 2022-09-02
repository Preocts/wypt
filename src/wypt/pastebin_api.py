"""API calls from Pastebin.com"""
from __future__ import annotations

import time

import httpx

# Cooldown, in seconds, required between scraping
SCRAPING_THROTTLE = 60
# Cooldown, in seconds, required between item scraping
ITEM_SCRAPING_THROTTLE = 1
# Cooldown, in seconds, required between item meta scraping
META_SCRAPING_THROTTLE = 1


class PastebinAPI:
    def __init__(self, *, last_call: int | None = None) -> None:
        """
        Create API client for pastebin.

        Keyword Args:
            last_call: Unix time of last action. Defaults to 'now'
        """
        self._http = httpx.Client(timeout=3, follow_redirects=False)
        self._last_call = last_call if last_call is not None else int(time.time())

    @property
    def can_scrape(self) -> bool:
        """Boolean representing if a scrape request can be performed."""
        return self._can_act(SCRAPING_THROTTLE)

    @property
    def can_scrape_item(self) -> bool:
        """Boolean representing if an item scrape can be performed."""
        return self._can_act(ITEM_SCRAPING_THROTTLE)

    @property
    def can_scrape_meta(self) -> bool:
        """Boolean representing if an meta scrape can be performed."""
        return self._can_act(META_SCRAPING_THROTTLE)

    def _can_act(self, timeout_seconds: int) -> bool:
        """Determine if enough time has lapsed to allow action."""
        return int(time.time()) - self._last_call >= timeout_seconds

    def scrape(self, limit: int = 100) -> list[dict[str, str]]:
        """
        Scrape recent posts from pastebin.

        Use the `.can_scrape` property to avoid raising a ThrottleError. If
        the limit is not a valid int, the default is used.

        Args:
            limit: Number of posts to return in call. Max 250, default 100.

        Returns:
            List of dictionaries

        Raises:
            ThrottleError: Raised if cooldown between pulls is still active.
        """
        ...
