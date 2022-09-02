from __future__ import annotations

import time

import pytest
from wypt.exceptions import ThrottleError
from wypt.pastebin_api import PastebinAPI


@pytest.fixture
def open_client() -> PastebinAPI:
    # Time is offset to the past to all throttles are open
    return PastebinAPI(last_call=0)


@pytest.fixture
def throttled_client() -> PastebinAPI:
    # Time is offset to the future so all throttles are closed
    return PastebinAPI(last_call=int(time.time()) + 1_000)


@pytest.mark.parametrize(("offset", "expected"), ((-1_000, True), (1_000, False)))
def test_can_act_on_init_with_offsets_of_last_call(offset: int, expected: bool) -> None:
    last_call = int(time.time()) + offset
    client = PastebinAPI(last_call=last_call)

    assert client.can_scrape is expected
    assert client.can_scrape_item is expected
    assert client.can_scrape_meta is expected


def test_scrape_raises_throttle_error(throttled_client: PastebinAPI) -> None:

    with pytest.raises(ThrottleError):
        throttled_client.scrape()


def test_scrape_returns_emtpy_on_raise_disabled(throttled_client: PastebinAPI) -> None:

    result = throttled_client.scrape(raise_on_throttle=False)

    assert result == []
