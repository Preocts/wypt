from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest
from httpx import Response
from wypt.exceptions import ResponseError
from wypt.exceptions import ThrottleError
from wypt.model import PasteMeta
from wypt.pastebin_api import DEFAULT_LIMIT
from wypt.pastebin_api import PastebinAPI

SCRAPE_RESP = Path("tests/fixture/scrape_resp.json").read_text()


@pytest.fixture
def client() -> PastebinAPI:
    # Time is offset to the past to all throttles are open
    return PastebinAPI(last_call=int(time.time()) - 1_000)


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


def test_scrape_raises_response_error_on_failure(client: PastebinAPI) -> None:
    resp = Response(404)

    with patch.object(client._http, "get", return_value=resp) as mock_http:

        with pytest.raises(ResponseError):
            client.scrape()

        assert mock_http.call_count == 1


def test_scrape_returns_on_success(client: PastebinAPI) -> None:

    resp = Response(200, content=SCRAPE_RESP)

    with patch.object(client._http, "get", return_value=resp) as mock_http:

        result = client.scrape(lang="json")
        kwargs = mock_http.call_args[1]  # use .kwargs after 3.7 dropped

        assert mock_http.call_count == 1
        assert len(result) == len(json.loads(SCRAPE_RESP))
        assert all([isinstance(r, PasteMeta) for r in result])
        assert kwargs["params"]["lang"] == "json"


@pytest.mark.parametrize(
    ("limit", "expected"),
    (
        (None, DEFAULT_LIMIT),
        (100, 100),
        (1, 1),
        (250, 250),
        (0, DEFAULT_LIMIT),
        (251, DEFAULT_LIMIT),
    ),
)
def test_scrape_limits(client: PastebinAPI, limit: int | None, expected: int) -> None:
    resp = Response(200, content=SCRAPE_RESP)

    with patch.object(client._http, "get", return_value=resp) as mock_http:

        _ = client.scrape(limit=limit)
        kwargs = mock_http.call_args[1]  # use .kwargs after 3.7 dropped
        assert kwargs["params"]["limit"] == str(expected)


def test_scrape_item_raises_throttle_error(throttled_client: PastebinAPI) -> None:
    with pytest.raises(ThrottleError):
        throttled_client.scrape_item("mock")


def test_scrape_item_returns_emtpy_on_raise_disabled(
    throttled_client: PastebinAPI,
) -> None:
    result = throttled_client.scrape_item("mock", raise_on_throttle=False)

    assert result is None


def test_scrape_item_raises_response_error_on_failure(client: PastebinAPI) -> None:
    resp = Response(404)

    with patch.object(client._http, "get", return_value=resp) as mock_http:

        with pytest.raises(ResponseError):
            client.scrape_item("mock")

        assert mock_http.call_count == 1


def test_scrape_item_returns_on_success(client: PastebinAPI) -> None:

    resp = Response(200, content=SCRAPE_RESP)

    with patch.object(client._http, "get", return_value=resp) as mock_http:

        result = client.scrape_item("mock")

        assert mock_http.call_count == 1
        assert result
        assert result.key == "mock"
        assert result.content == SCRAPE_RESP


def test_scrape_meta_raises_throttle_error(throttled_client: PastebinAPI) -> None:
    with pytest.raises(ThrottleError):
        throttled_client.scrape_meta("mock")


def test_scrape_meta_returns_emtpy_on_raise_disabled(
    throttled_client: PastebinAPI,
) -> None:
    result = throttled_client.scrape_meta("mock", raise_on_throttle=False)

    assert result is None


def test_scrape_meta_raises_response_error_on_failure(client: PastebinAPI) -> None:
    resp = Response(404)

    with patch.object(client._http, "get", return_value=resp) as mock_http:

        with pytest.raises(ResponseError):
            client.scrape_meta("mock")

        assert mock_http.call_count == 1


def test_scrape_meta_returns_on_success(client: PastebinAPI) -> None:

    resps = json.loads(SCRAPE_RESP)
    resp = Response(200, content=json.dumps(resps[0]))

    with patch.object(client._http, "get", return_value=resp) as mock_http:

        result = client.scrape_meta("mock")

        assert mock_http.call_count == 1
        assert result
        assert result.to_dict() == resps[0]


def test_scrape_meta_returns_none_on_invalid_success(client: PastebinAPI) -> None:

    resp = Response(200, content="something went wrong")

    with patch.object(client._http, "get", return_value=resp) as mock_http:

        result = client.scrape_meta("mock")

        assert mock_http.call_count == 1
        assert result is None
