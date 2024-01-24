from __future__ import annotations

import datetime

import wypt._filters


def test_to_datetime_with_valid_timestamp() -> None:
    now = datetime.datetime.now()
    now_ts = str(now.timestamp())
    expected = now.strftime("%Y-%m-%d %H:%M:%S")

    result = wypt._filters._to_datetime(now_ts)

    assert expected == result


def test_to_datetime_with_invalid_timestamp() -> None:
    invalid_ts = "this isn't valid"

    result = wypt._filters._to_datetime(invalid_ts)

    assert invalid_ts == result
