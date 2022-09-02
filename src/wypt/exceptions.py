"""Custom exceptions for project."""
from __future__ import annotations

import time


class ThrottleError(Exception):
    def __init__(
        self,
        msg: str,
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
        self.msg = msg
        diff = int(time.time()) - (last_call or 0)
        super().__init__(f"{msg} - (Remaining cooldown: {diff} ({cooldown}")
