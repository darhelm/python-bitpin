"""Tests for the sync client, using the responses library."""

import json

import pytest
import responses
from responses import matchers

from bitpin import Client
from bitpin.exceptions import APIException

API = "https://api.bitpin.ir/api/v1"


@pytest.fixture
def mocked():
    with responses.RequestsMock() as rsps:
        rsps.post(f"{API}/usr/authenticate/", json={"refresh": "refresh-token", "access": "access-token"})
        yield rsps


@pytest.fixture
def client(mocked):
    return Client(api_key="key", api_secret="secret")


def test_failed_cancel_raises(client, mocked):
    mocked.delete(f"{API}/odr/orders/404/", json={"detail": "Not found."}, status=404)
    with pytest.raises(APIException) as info:
        client.cancel_order("404")
    assert info.value.status_code == 404


def test_cancel_with_empty_body(client, mocked):
    mocked.delete(f"{API}/odr/orders/7/", status=204)
    assert client.cancel_order("7") == {"status": "success", "id": "7"}


def test_orderbook_is_public(client, mocked):
    mocked.get(f"{API}/mth/orderbook/BTC_IRT/", json={"asks": [["100", "1"]], "bids": []})
    assert client.get_orderbook("BTC_IRT")["asks"] == [["100", "1"]]
    assert "Authorization" not in mocked.calls[-1].request.headers


def test_user_orders_query_params(client, mocked):
    mocked.get(
        f"{API}/odr/orders/",
        json=[],
        match=[
            matchers.query_param_matcher(
                {"symbol": "BTC_IRT", "state": ["active", "initial"], "identifiers_in": "a,b"},
            )
        ],
    )
    assert client.get_user_orders(symbol="BTC_IRT", state=["active", "initial"], identifiers_in=["a", "b"]) == []


def test_user_trades_uses_fills(client, mocked):
    mocked.get(f"{API}/odr/fills/", json=[{"id": 1}])
    assert client.get_user_trades() == [{"id": 1}]


def test_get_order(client, mocked):
    mocked.get(f"{API}/odr/orders/42/", json={"id": 42, "state": "active"})
    assert client.get_order("42")["state"] == "active"


def test_bulk_cancel_body(client, mocked):
    mocked.delete(f"{API}/odr/orders/bulk/", json={"canceled_orders": ["1"], "not_canceled_orders": []})
    client.cancel_order_bulk(identifiers=["a"])
    assert json.loads(mocked.calls[-1].request.body) == {"identifiers": ["a"]}
