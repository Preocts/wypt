"""Custom filters applied in Jinja2 templates."""
from __future__ import annotations

import datetime

from fastapi.templating import Jinja2Templates


def _to_datetime(timestamp: str) -> str:
    """Translate a timestamp to datetime string."""
    try:
        _timestamp = float(timestamp)
    except ValueError:
        # Return what we were given if this fails to convert
        # This is processed in the Jinja2 template so no need for error raising
        return timestamp

    dateobj = datetime.datetime.fromtimestamp(_timestamp)

    return dateobj.strftime("%Y-%m-%d %H:%M:%S")


def apply_filters(template: Jinja2Templates) -> None:
    """Apply all defined filters to the template."""
    template.env.filters["to_datetime"] = _to_datetime
