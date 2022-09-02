from __future__ import annotations

import time

from wypt.pastebin_api import PastebinAPI


def test_can_act_on_init_with_last_call_in_past() -> None:
    client = PastebinAPI(last_call=0)

    assert client.can_scrape is True
    assert client.can_scrape_item is True
    assert client.can_scrape_meta is True


def test_can_act_is_false_with_last_call_in_future() -> None:
    client = PastebinAPI(last_call=int(time.time()) + 1_000)

    assert client.can_scrape is False
    assert client.can_scrape_item is False
    assert client.can_scrape_meta is False
