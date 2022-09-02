"""API calls from Pastebin.com"""
from __future__ import annotations

import logging
import time

import httpx

from .exceptions import ResponseError
from .exceptions import ThrottleError
from .model import Paste

# Cooldown, in seconds, required between scraping
SCRAPING_THROTTLE = 60
# Cooldown, in seconds, required between item scraping
ITEM_SCRAPING_THROTTLE = 1
# Cooldown, in seconds, required between item meta scraping
META_SCRAPING_THROTTLE = 1
DEFAULT_LIMIT = 100


class PastebinAPI:

    logger = logging.getLogger(__name__)
    base_url = "https://scrape.pastebin.com"

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

    def scrape(
        self,
        limit: int | None = None,
        lang: str | None = None,
        *,
        raise_on_throttle: bool = True,
    ) -> list[Paste]:
        """
        Scrape recent posts from pastebin.

        Use the `.can_scrape` property to avoid raising a ThrottleError. If
        the limit is not a valid int, the default is used.

        Language filters supported: https://pastebin.com/doc_api#5

        Args:
            limit: Number of posts to return in call. Max 250, default 100.
            lang: Filter results by language.
            raise_on_throttle: If False and throttled an empty list will be returned.

        Returns:
            List of Paste objects.

        Raises:
            ThrottleError: Raised if cooldown between pulls is still active.
            ResponseError: Raised if pastebin returns a failure response.
        """
        if not self.can_scrape:
            if raise_on_throttle:
                raise ThrottleError(
                    "Scrape throttle has not expired",
                    self._last_call,
                    SCRAPING_THROTTLE,
                )
            else:
                return []
        limit = limit if limit and limit > 0 and limit < 250 else DEFAULT_LIMIT
        params = {"limit": str(limit)}
        params.update({"lang": lang} if lang else {})

        self.logger.debug("Requesting api_scraping.php with %s params", params)

        resp = self._http.get(f"{self.base_url}/api_scraping.php", params=params)

        if not resp.is_success:
            self.logger.error(
                "Invalid response on scrape attempt. %s - %s",
                resp.status_code,
                resp.text,
            )
            raise ResponseError(resp.text, "GET", resp.status_code)

        models = [Paste(**paste) for paste in resp.json()]

        self.logger.debug("Discovered %d pastes from request.", len(models))

        return models
