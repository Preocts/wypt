"""Custom exceptions for project."""

from __future__ import annotations

import time


class ThrottleError(Exception):
    def __init__(
        self,
        last_call: int | None = None,
        cooldown: int | None = None,
    ) -> None:
        """
        Raise when action is not permitted by cooldown window.

        Args:
            msg: Text of exception message
            last_call: Unix seconds since last call
            cooldown: Cooldown seconds
        """
        self.last_call = last_call
        self.cooldown = cooldown
        self.msg = "Item Scrape throttle has not expired"

        diff = int(time.time()) - (last_call or 0)
        super().__init__(f"{self.msg} - (Remaining cooldown: {diff} ({cooldown}")


class ResponseError(Exception):
    def __init__(
        self,
        msg: str,
        method: str | None = None,
        status_code: int | None = None,
    ) -> None:
        """
        Raise on failed calls.

        Args:
            msg: Text of exception message
            method: Verb of API call (e.g. "POST")
            status_code: Result of API call
        """
        self.method = method
        self.status_code = status_code
        self.msg = msg
        super().__init__(f"[{status_code}] - {str(method).upper()} - {msg}")
