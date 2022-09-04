"""
API calls from Pastebin.com

All methods in this function require that your account be Pro and
allowlisted in pastebin's setup. https://pastebin.com/doc_scraping_api

Scraping endpoints of pastebin do not, generally, return error statuses
even on invalid requests. Due to this, any error status will raise a
ResponseError exception.
"""
from __future__ import annotations

import json
import logging
import time
from typing import NoReturn

import httpx

from .exceptions import ResponseError
from .exceptions import ThrottleError
from .model import PasteMeta

# Cooldown, in seconds, required between scraping
SCRAPING_THROTTLE = 60
# Cooldown, in seconds, required between item scraping
ITEM_THROTTLE = 1
# Cooldown, in seconds, required between item meta scraping
META_THROTTLE = 1
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
        return self._can_act(ITEM_THROTTLE)

    @property
    def can_scrape_meta(self) -> bool:
        """Boolean representing if an meta scrape can be performed."""
        return self._can_act(META_THROTTLE)

    def _can_act(self, timeout_seconds: int) -> bool:
        """Determine if enough time has lapsed to allow action."""
        return int(time.time()) - self._last_call >= timeout_seconds

    def scrape(
        self,
        limit: int | None = None,
        lang: str | None = None,
        *,
        raise_on_throttle: bool = True,
    ) -> list[PasteMeta]:
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
        if not self._can_run_action(SCRAPING_THROTTLE, raise_on_throttle):
            return []

        limit = limit if limit and 0 < limit <= 250 else DEFAULT_LIMIT
        params = {"limit": str(limit)}
        if lang:
            params.update({"lang": lang})

        resp = self._get_request("api_scraping.php", params)
        models = [PasteMeta(**paste) for paste in resp.json()]
        self.logger.debug("Discovered %d pastes from request.", len(models))
        return models

    def scrape_item(self, key: str, *, raise_on_throttle: bool = True) -> str | None:
        """
        Scrape a specific post by item key.

        Use the `.can_scrape_item` property to avoid raising a
        ThrottleError. If the limit is not a valid int, the default is used.

        Args:
            key: Unique paste key.
            raise_on_throttle: If False and throttled then None will be returned.

        Returns:
            String of paste.

        Raises:
            ThrottleError: Raised if cooldown between pulls is still active.
            ResponseError: Raised if pastebin returns a failure response.
        """
        if not self._can_run_action(ITEM_THROTTLE, raise_on_throttle):
            return None

        params = {"i": key}
        resp = self._get_request("api_scraping_item.php", params)
        return resp.text

    def scrape_meta(
        self,
        key: str,
        *,
        raise_on_throttle: bool = True,
    ) -> PasteMeta | None:
        """
        Scrape meta of a paste by unique paste key.

        Use the `.can_scrape_meta` property to avoid raising a
        ThrottleError. If the limit is not a valid int, the default is used.

        Args:
            key: Unique paste key.
            raise_on_throttle: If False and throttled then None will be returned.

        Returns:
            A Paste object or None.

        Raises:
            ThrottleError: Raised if cooldown between pulls is still active.
            ResponseError: Raised if pastebin returns a failure response.
        """
        if not self._can_run_action(META_THROTTLE, raise_on_throttle):
            return None

        params = {"i": key}

        resp = self._get_request("api_scraping_meta.php", params)

        try:
            return PasteMeta(**resp.json())
        except (TypeError, json.JSONDecodeError):
            return None

    def _can_run_action(self, cooldown: int, raise_: bool) -> bool:
        """Check throttle, raise if desired."""
        throttled = self._can_act(cooldown)
        if not throttled and raise_:
            raise ThrottleError(self._last_call, cooldown)
        return throttled

    def _response_error(self, text: str, code: int) -> NoReturn:
        """Handle logging and raising on response error."""
        self.logger.error("Invalid response on scrape attempt. %d - %s", code, text)
        raise ResponseError(text, "GET", code)

    def _get_request(
        self,
        route: str,
        params: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Handle GET request to pastebin."""
        url = f"{self.base_url}/{route}"
        self.logger.debug("GET - %s - with %s", url, params)
        resp = self._http.get(url, params=params)
        self._last_call = int(time.time())

        if not resp.is_success:
            self._response_error(resp.text, resp.status_code)
        return resp
