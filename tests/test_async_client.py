"""Tests for the async client, run against a local aiohttp server."""

import json

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from bitpin import AsyncClient
from bitpin.exceptions import APIException


class Recorder:
    """Keeps the requests the fake server received."""

    def __init__(self) -> None:
        self.requests: list[web.Request] = []
        self.bodies: list[object] = []


def build_app(recorder: Recorder) -> web.Application:
    async def record(request: web.Request) -> None:
        recorder.requests.append(request)
        text = await request.text()
        recorder.bodies.append(json.loads(text) if text else None)

    async def authenticate(request: web.Request) -> web.Response:
        await record(request)
        return web.json_response({"refresh": "refresh-token", "access": "access-token"})

    async def orderbook(request: web.Request) -> web.Response:
        await record(request)
        return web.json_response({"asks": [["100", "1.5"]], "bids": [["99", "2"]]})

    async def orders(request: web.Request) -> web.Response:
        await record(request)
        return web.json_response([])

    async def fills(request: web.Request) -> web.Response:
        await record(request)
        return web.json_response([{"id": 1}])

    async def order(request: web.Request) -> web.Response:
        await record(request)
        order_id = request.match_info["order_id"]
        if request.method == "DELETE":
            if order_id == "404":
                return web.json_response({"detail": "Not found."}, status=404)
            return web.Response(status=204)
        return web.json_response({"id": int(order_id), "state": "closed", "dealed_base_amount": "1"})

    async def bulk(request: web.Request) -> web.Response:
        await record(request)
        if request.method == "DELETE":
            return web.json_response({"canceled_orders": ["1"], "not_canceled_orders": []})
        return web.json_response([{"id": 1}, {"id": 2}])

    app = web.Application()
    app.router.add_post("/api/v1/usr/authenticate/", authenticate)
    app.router.add_get("/api/v1/mth/orderbook/{symbol}/", orderbook)
    app.router.add_get("/api/v1/odr/orders/", orders)
    app.router.add_get("/api/v1/odr/fills/", fills)

    async def markets(request: web.Request) -> web.Response:
        return web.Response(status=503, text="<h1>Server Error (503)</h1>")

    app.router.add_get("/api/v1/mkt/markets/", markets)
    app.router.add_route("*", "/api/v1/odr/orders/bulk/", bulk)
    app.router.add_route("*", "/api/v1/odr/orders/{order_id}/", order)
    return app


@pytest.fixture
async def server():
    recorder = Recorder()
    test_server = TestServer(build_app(recorder))
    await test_server.start_server()
    yield test_server, recorder
    await test_server.close()


@pytest.fixture
async def client(server, monkeypatch):
    test_server, _ = server
    monkeypatch.setattr(AsyncClient, "API_URL", str(test_server.make_url("/api")))
    bitpin = await AsyncClient.create(api_key="key", api_secret="secret")
    yield bitpin
    await bitpin.close_connection()


async def test_login_stores_tokens(client):
    assert client.access_token == "access-token"
    assert client.refresh_token == "refresh-token"


async def test_orderbook_is_public(client, server):
    _, recorder = server
    book = await client.get_orderbook("BTC_IRT")
    assert book == {"asks": [["100", "1.5"]], "bids": [["99", "2"]]}
    assert "Authorization" not in recorder.requests[-1].headers


async def test_failed_cancel_raises(client):
    with pytest.raises(APIException) as info:
        await client.cancel_order("404")
    assert info.value.status_code == 404


async def test_cancel_with_empty_body(client):
    assert await client.cancel_order("7") == {"status": "success", "id": "7"}


async def test_user_orders_query_params(client, server):
    _, recorder = server
    await client.get_user_orders(symbol="BTC_IRT", side=["buy", "sell"], ids_in=["1", "2"], limit=10)
    query = recorder.requests[-1].query
    assert query.getall("side") == ["buy", "sell"]
    assert query["ids_in"] == "1,2"
    assert query["symbol"] == "BTC_IRT"
    assert query["limit"] == "10"
    assert "offset" not in query


async def test_user_trades_uses_fills(client, server):
    _, recorder = server
    assert await client.get_user_trades(symbol="BTC_IRT") == [{"id": 1}]
    assert recorder.requests[-1].path == "/api/v1/odr/fills/"


async def test_get_order(client, server):
    _, recorder = server
    result = await client.get_order("42")
    assert result["id"] == 42
    assert recorder.requests[-1].path == "/api/v1/odr/orders/42/"


async def test_bulk_bodies_are_json(client, server):
    _, recorder = server
    orders = [
        {"symbol": "USDT_IRT", "base_amount": 1, "price": 100, "side": "buy", "type": "limit"},
        {"symbol": "USDT_IRT", "base_amount": 2, "price": 99, "side": "buy", "type": "limit"},
    ]
    await client.create_order_bulk(orders)
    assert recorder.bodies[-1] == orders

    await client.cancel_order_bulk(ids=[1, 2])
    assert recorder.bodies[-1] == {"ids": ["1", "2"]}


async def test_bulk_cancel_needs_ids(client):
    with pytest.raises(ValueError):
        await client.cancel_order_bulk()


async def test_non_json_error_keeps_body(client):
    with pytest.raises(APIException) as info:
        await client.get_markets_info()
    assert "Server Error" in str(info.value)
    assert "bound method" not in str(info.value)
