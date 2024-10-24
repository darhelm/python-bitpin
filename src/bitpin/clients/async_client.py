"""# Bitpin Async Client."""

# pylint: disable=invalid-overridden-method

import asyncio
from warnings import warn

import aiohttp

from .. import enums
from .. import response_types as t
from .._utils import get_loop
from ..exceptions import (
    APIException,
    RequestException,
)
from .core import CoreClient


class AsyncClient(CoreClient):
    """
    Async Client.

    Methods:
        login: Login and set (refresh_token/access_token)
        refresh_access_token: Refresh token.
        get_currencies_info: Get currencies info.
        get_markets_info: Get markets info.
        get_tickets_info: Get tickets info.
        get_wallets: Get wallets.
        get_orderbook: Get orderbook.
        get_recent_trades: Get recent trades.
        get_user_orders: Get user orders.
        create_order: Create order.
        cancel_order: Cancel order.
        create_order_bulk: Create Bulk Order.
        cancel_order_bulk: Cancel Bulk Order.
        get_user_trades: Get user trades.
        close_connection: Close connection.

    Attributes:
        session (aiohttp.ClientSession): Session.
        loop (asyncio.AbstractEventLoop): Event Loop
        api_key (str): API key.
        api_secret (str): API secret.
        refresh_token (str): Refresh token.
        access_token (str): Access token.
    """

    def __init__(  # type: ignore[no-untyped-def]
        self,
        api_key: t.OptionalStr = None,
        api_secret: t.OptionalStr = None,
        access_token: t.OptionalStr = None,
        refresh_token: t.OptionalStr = None,
        requests_params: t.OptionalDictStrAny = None,
        session_params: t.OptionalDictStrAny = None,
        loop: t.OptionalEventLoop = None,
        background_relogin: bool = False,
        background_relogin_interval: int = 60 * 60 * 24 * 6,
        background_refresh_token: bool = False,
        background_refresh_token_interval: int = 60 * 13,
    ):
        """
        Constructor.

        Args:
            api_key (str): API key.
            api_secret (str): API secret.
            access_token (str): Access token.
            refresh_token (str): Refresh token.
            requests_params (dict): Requests params.
            session_params (dict): Session params.
            loop (asyncio.AbstractEventLoop): Event loop.
            background_relogin (bool): Background refresh.
            background_relogin_interval (int): Background refresh interval.
            background_refresh_token (bool): Background refresh token.
            background_refresh_token_interval (int): Background refresh token interval.

        Notes:
            If `api_key` and `api_secret` are not provided, they will be read from the environment variables
            `BITPIN_API_KEY` and `BITPIN_API_SECRET` respectively.

            If `access_token` and `refresh_token` are not provided, they will be read from the environment variables
            `BITPIN_ACCESS_TOKEN` and `BITPIN_REFRESH_TOKEN` respectively.

            If `requests_params` are provided, they will be used as default for every request.

            If `requests_params` are provided in `kwargs`, they will override existing `requests_params`.

            If `background_relogin` is enabled, access token will be refreshed in background every
            `background_relogin_interval` seconds.

            If `background_refresh_token` is enabled, refresh token will be refreshed in background every
            `background_refresh_token_interval` seconds.
        """

        self.loop = loop or get_loop()
        self._session_params = session_params or {}

        super().__init__(
            api_key,
            api_secret,
            access_token,
            refresh_token,
            requests_params,
            background_relogin,
            background_relogin_interval,
            background_refresh_token,
            background_refresh_token_interval,
        )

    @classmethod
    async def create(  # type: ignore[no-untyped-def]
        cls,
        api_key: t.OptionalStr = None,
        api_secret: t.OptionalStr = None,
        access_token: t.OptionalStr = None,
        refresh_token: t.OptionalStr = None,
        requests_params: t.OptionalDictStrAny = None,
        session_params: t.OptionalDictStrAny = None,
        loop: t.OptionalEventLoop = None,
        background_relogin: bool = False,
        background_relogin_interval: int = 60 * 60 * 24 * 6,
        background_refresh_token: bool = False,
        background_refresh_token_interval: int = 60 * 13,
    ) -> "AsyncClient":
        """
        Create AsyncClient.

        Args:
            api_key (str): API key.
            api_secret (str): API secret.
            access_token (str): Access token.
            refresh_token (str): Refresh token.
            requests_params (dict): Requests params.
            session_params (dict): Session params.
            loop (asyncio.AbstractEventLoop): Event loop.
            background_relogin (bool): Background refresh.
            background_relogin_interval (int): Background refresh interval.
            background_refresh_token (bool): Background refresh token.
            background_refresh_token_interval (int): Background refresh token interval.

        Returns:
            AsyncClient: AsyncClient.
        """

        self = cls(
            api_key,
            api_secret,
            access_token,
            refresh_token,
            requests_params,
            session_params,
            loop,
            background_relogin,
            background_relogin_interval,
            background_refresh_token,
            background_refresh_token_interval,
        )

        await self._handle_login()
        return self

    def _init_session(self) -> aiohttp.ClientSession:
        """
        Initialize session.

        Returns:
            session (aiohttp.ClientSession): Session.

        """

        session = aiohttp.ClientSession(
            loop=self.loop,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            **self._session_params,
        )
        return session

    async def _get(  # type: ignore[no-untyped-def, override]
        self,
        path: str,
        signed: bool = False,
        version: str = CoreClient.PUBLIC_API_VERSION_1,
        **kwargs,
    ) -> t.DictStrAny:
        """
        Make a GET request.

        Args:
            path (str): Path.
            signed (bool): Signed.
            version (str): Version.
            **kwargs: Kwargs.

        Returns:
            dict: Response.
        """

        return await self._request_api(
            enums.RequestMethod.GET, path, signed, version, **kwargs
        )

    async def _post(  # type: ignore[no-untyped-def, override]
        self,
        path: str,
        signed: bool = False,
        version: str = CoreClient.PUBLIC_API_VERSION_1,
        **kwargs,
    ) -> t.DictStrAny:
        """
        Make a POST request.

        Args:
            path (str): Path.
            signed (bool): Signed.
            version (str): Version.
            **kwargs: Kwargs.

        Returns:
            dict: Response.
        """

        return await self._request_api(
            enums.RequestMethod.POST, path, signed, version, **kwargs
        )

    async def _delete(  # type: ignore[no-untyped-def, override]
        self,
        path: str,
        signed: bool = False,
        version: str = CoreClient.PUBLIC_API_VERSION_1,
        **kwargs,
    ) -> t.DictStrAny:
        """
        Make a DELETE request.

        Args:
            path (str): Path.
            signed (bool): Signed.
            version (str): Version.
            **kwargs: Kwargs.

        Returns:
            dict: Response.
        """

        return await self._request_api(
            enums.RequestMethod.DELETE, path, signed, version, **kwargs
        )

    async def _request_api(  # type: ignore[no-untyped-def, override]
        self,
        method: t.RequestMethods,
        path: str,
        signed: bool = False,
        version: str = CoreClient.PUBLIC_API_VERSION_1,
        **kwargs,
    ) -> t.DictStrAny:
        """
        Request API.

        Args:
            method (RequestMethod): Method.
            path (str): Path.
            signed (bool): Signed.
            version (str): Version.
            **kwargs: Kwargs.

        Returns:
            dict: Response.
        """

        uri = self._create_api_uri(path, version)
        return await self._request(method, uri, signed, **kwargs)

    async def _request(  # type: ignore[no-untyped-def, override]
        self, method: t.RequestMethods, uri: str, signed: bool, **kwargs
    ) -> t.DictStrAny:
        """
        Request.

        Args:
            method (RequestMethod): Method.
            uri (str): URI.
            signed (bool): Signed.
            **kwargs: Kwargs.

        Returns:
            dict: Response.
        """

        kwargs = self._get_request_kwargs(method, signed, **kwargs)

        async with getattr(self.session, method)(uri, **kwargs) as response:
            self.response = response  # pylint: disable=attribute-defined-outside-init
            return await self._handle_response(response)

    @staticmethod
    async def _handle_response(response: aiohttp.ClientResponse) -> t.DictStrAny:  # type: ignore[override]
        """
        Handle response.

        Args:
            response (aiohttp.ClientResponse): Response.

        Returns:
            dict: Response.

        Raises:
            APIException: API Exception.
            RequestException: Request Exception.
        """

        if not str(response.status).startswith("2"):
            raise APIException(response, response.status, await response.text())
        try:
            if response.method.lower() == enums.RequestMethod.DELETE:
                return {"status": "success", "id": response.request_info.url.parts[-2]}
            return await response.json()  # type: ignore[no-any-return]
        except ValueError as exc:
            msg = f"Invalid Response: {await response.text()}"
            raise RequestException(msg) from exc

    async def _background_relogin_task(self) -> None:  # type: ignore[override]
        """Background relogin task."""

        while True:
            try:
                await self.login()
                await asyncio.sleep(self._background_relogin_interval)
            except Exception:  # pylint: disable=broad-except
                continue

    async def _background_refresh_token_task(self) -> None:  # type: ignore[override]
        """Background refresh token task."""

        while True:
            try:
                await self.refresh_access_token()
                await asyncio.sleep(self._background_refresh_token_interval)
            except Exception:  # pylint: disable=broad-except
                continue

    async def _handle_login(self) -> None:  # type: ignore[override]
        """Handle login."""

        if self.api_key and self.api_secret:
            await self.login()

        if self._background_relogin:
            self.loop.create_task(self._background_relogin_task())

        if self._background_refresh_token:
            self.loop.create_task(self._background_refresh_token_task())

    async def login(self, **kwargs) -> t.LoginResponse:  # type: ignore[no-untyped-def, override]
        """
        Login and set (refresh_token/access_token).

        Args:
            **kwargs: Kwargs.

        Returns:
            Response (LoginResponse): Response.

        References:
            [API Docs](https://docs.bitpin.ir/v1/docs/authentication/intro)
        """

        kwargs["json"] = {"api_key": self.api_key, "secret_key": self.api_secret}
        _: t.LoginResponse = await self._post(self.LOGIN_URL, **kwargs)  # type: ignore[assignment]

        self.refresh_token = _["refresh"]
        self.access_token = _["access"]

        return _

    async def refresh_access_token(  # type: ignore[no-untyped-def, override]
        self, refresh_token: t.OptionalStr = None, **kwargs
    ) -> t.RefreshTokenResponse:
        """
        Refresh token.

        Args:
            refresh_token (str): Refresh token.
            **kwargs: Kwargs.

        Returns:
            Response (RefreshTokenResponse): Response.

        References:
            [API Docs](https://docs.bitpin.ir/v1/docs/authentication/refresh_token)
        """

        kwargs["json"] = {"refresh": refresh_token or self.refresh_token}
        _: t.RefreshTokenResponse = await self._post(self.REFRESH_TOKEN_URL, **kwargs)  # type: ignore[assignment]

        self.access_token = _["access"]

        return _

    # Deprecated Methods
    async def get_user_info(self, **kwargs) -> None:  # type: ignore[no-untyped-def, override]
        """
        Get user info (DEPRECATED).
        """

        warn(
            "get_user_info is deprecated! if deprecated method's usage is still in need import client from bitpin.deprecated instead!",
            DeprecationWarning,
            2,
        )

    # Working Methods
    async def get_currencies_info(  # type: ignore[no-untyped-def, override]
        self,
    ) -> t.CurrenciesInfo:
        """
        Get currencies info.

        Returns:
            Response (dict): Response.

        References:
            [API Docs](https://docs.bitpin.ir/v1/docs/market-data/currencies)

        Notes:
            Rate limit: 10000/day or 200/minute if you are authenticated.
        """

        return await self._get(self.CURRENCIES_LIST_URL)

    async def get_markets_info(self) -> t.MarketsInfo:  # type: ignore[no-untyped-def, override]
        """
        Get markets info.

        Returns:
            Response (dict): Response.

        References:
            [API Docs](https://docs.bitpin.ir/v1/docs/market-data/markets)

        Notes:
            Rate limit: 10000/day or 200/minute if you are authenticated.
        """

        return await self._get(self.MARKETS_LIST_URL)

    async def get_tickers_info(self) -> t.DictStrAny:
        """
        Get tickets info.

        Returns:
            Response (dict): Response.

        References:
            [API Docs](https://docs.bitpin.ir/v1/docs/market-data/tickers)

        Notes:
            Rate limit: 80/minute .
        """

        return await self._get(self.TICKERS_LIST_URL)

    async def get_wallets(  # type: ignore[no-untyped-def, override]
        self,
        assets: t.OptionalStr = None,
        service: t.OptionalStr = None,
        offset: t.OptionalInt = None,
        limit: t.OptionalInt = None,
        **kwargs,
    ) -> t.WalletInfo:
        """
        Get wallets.

        Args:
            assets: asset name [BTC, IRT, USDT, ...]
            service: name of service
            offset: asset balance offset, i.e. assets below 10000
            limit: maximum received assets info

        Returns:
            Response (dict): Response.

        References:
            [API Docs](https://docs.bitpin.ir/v1/docs/wallets)

        Notes:
            Rate limit: 10000/day.
        """

        kwargs["params"] = {
            k: str(v)
            for k, v in locals().items()
            if v is not None and k not in {"self", "kwargs"}
        }
        return await self._get(self.WALLETS_URL, signed=True, **kwargs)

    async def get_orderbook(  # type: ignore[no-untyped-def, override]
        self,
        symbol: str,
    ) -> t.OrderbookResponse:
        """
        Get orderbook.

        Args:
            symbol (str): i.e. BTC_IRT, ETH_USDT

        Returns:
            Response (dict): Response.

        References:
            [API Docs](https://docs.bitpin.ir/v1/docs/market-data/orderbook)

        Notes:
            Rate Limit: 60 Requests/minute
        """

        return await self._get(  # type: ignore[return-value]
            self.ORDERBOOK_URL.format(symbol, str(type)),
            version=self.PUBLIC_API_VERSION_1,
        )

    async def get_recent_trades(  # type: ignore[no-untyped-def, override]
        self, symbol: str
    ) -> t.RecentTradesInfo:
        """
        Get recent trades.

        Args:
            symbol (str): i.e. BTC_IRT.

        Returns:
            Response (dict): Response.

        References:
            [API Docs](https://docs.bitpin.ir/v1/docs/market-data/matches)

        Notes:
            Rate Limit: 60 requests/minute
        """

        return await self._get(self.RECENT_TRADES_URL.format(symbol))  # type: ignore[return-value]

    async def get_user_orders(  # type: ignore[no-untyped-def, override]
        self,
        symbol: t.OptionalStr = None,
        side: t.OptionalOrderTypesList = None,  # pylint: disable=redefined-builtin
        state: t.OptionalOrderStateList = None,
        type: t.OptionalOrderModesList = None,
        identifier: t.OptionalStr = None,
        start: t.OptionalDate = None,
        end: t.OptionalDate = None,
        ids_in: t.OptionalStrList = None,
        identifiers_in: t.OptionalStrList = None,
        offset: t.OptionalInt = None,
        limit: t.OptionalInt = None,
        **kwargs,
    ) -> t.OpenOrdersResponse:
        """
        Get user orders.

        Args:
            symbol (Optional[str]): symbol (e.g., BTC_IRT, ETH_USDT). Defaults to None.
            side (Optional[List[str]]): The type of order, either 'buy' or 'sell'. Defaults to None.
            state (Optional[List[str]]): The state of the order, can be 'initial', 'active', or 'closed'. Defaults to None.
            type (Optional[List[str]]): The type of the order, can be 'limit', 'market', 'stop_limit', or 'oco'. Defaults to None.
            identifier (Optional[str]): A unique identifier for the order, useful for tracking or preventing duplicate entries. Defaults to None.
            start (Optional[date]): Show orders created after this date. Defaults to None.
            end (Optional[date]): Show orders created before this date. Defaults to None.
            ids_in (Optional[List[str]]): A list of order IDs to filter results. Defaults to None.
            identifiers_in (Optional[List[str]]): A list of specific order identifiers to filter results. Defaults to None.
            offset (Optional[int]): Show orders with IDs less than this value. Defaults to None.
            limit (Optional[int]): The maximum number of orders to retrieve (maximum: 100). Defaults to None.
            **kwargs: Kwargs.

        Returns:
            Response (dict): Response.

        References:
            [API Docs](https://docs.bitpin.ir/v1/docs/order/get_order_list)

        Notes:
            Rate Limit: 80 Requests/minute
        """

        kwargs["params"] = kwargs.get("params", {})
        kwargs["params"].update(
            {
                k: str(v)
                for k, v in locals().items()
                if v is not None and k not in {"self", "kwargs"}
            }
        )
        return await self._get(self.ORDERS_URL, signed=True, **kwargs)  # type: ignore[return-value]

    async def create_order(  # type: ignore[no-untyped-def, override]
        self,
        symbol: str,
        type: t.OrderModes,
        side: t.OrderTypes,  # pylint: disable=redefined-builtin
        base_amount: float,
        quote_amount: t.OptionalFloat = None,
        price: t.OptionalFloat = None,
        stop_price: t.OptionalFloat = None,
        oco_target_price: t.OptionalFloat = None,
        identifier: t.OptionalStr = None,
        **kwargs,
    ) -> t.CreateOrderResponse:
        """
        Create order.

        Args:
            symbol (str): i.e. [USDT_IRT]
            type: t.OrderModes
            side: t.OrderTypes
            price: float
            base_amount: float
            quote_amount: t.OptionalFloat = None
            stop_price: t.OptionalFloat = None
            oco_target_price: t.OptionalFloat = None
            identifier: t.OptionalStr = None
            **kwargs: Kwargs.

        Returns:
            Response (dict): Response.

        References:
            [API Docs](https://docs.bitpin.ir/v1/docs/order/place_order)

        Notes:
            Rate Limit: 5400 Requests/hour
        """

        kwargs["json"] = {
            "symbol": symbol,
            "type": type,
            "side": side,
            "price": price,
            "base_amount": base_amount,
            "quote_amount": quote_amount,
            "stop_price": stop_price,
            "oco_target_price": oco_target_price,
            "identifier": identifier,
        }

        kwargs["json"] = {k: v for k, v in kwargs["json"].items() if v is not None}
        return await self._post(self.ORDERS_URL, signed=True, **kwargs)  # type: ignore[return-value]

    async def cancel_order(  # type: ignore[no-untyped-def, override]
        self, order_id: str, **kwargs
    ) -> t.CancelOrderResponse:
        """
        Cancel order.

        Args:
            order_id (str): Order ID.
            **kwargs: Kwargs.

        Returns:
            Response (dict): Response.

        References:
            [API Docs](https://docs.bitpin.ir/v1/docs/order/cancel)

        Notes:
            Rate Limit: 5400 Requests/hour
        """

        try:
            await self._delete(self.ORDERS_URL + f"{order_id}/", signed=True, **kwargs)  # type: ignore[return-value]
        except APIException as e:
            raise e from e
        else:
            return {"status": "success", "id": order_id}

    async def create_order_bulk(self, orders: t.BulkOrderList, **kwargs):
        """
        Create multiple orders in bulk.

        Args:
            orders (BulkOrderList): A list of order objects to be created in bulk.
                Each order object (dict) should contain:
                    - symbol (str): The market symbol for the order (e.g., USDT_IRT).
                    - base_amount (float): The amount of the base asset to be ordered.
                    - price (float): The price at which the order is placed (for limit orders).
                    - side (str): The side of the order, either 'buy' or 'sell'.
                    - type (str): The type of the order, such as 'limit', 'market', etc.
            **kwargs: Additional parameters to be passed in the request.

        Returns:
            Response (dict): Response.

        limitations:
            - a maximum of 10 orders can be placed at a time
            - all orders must be in the same market
            - if one wrong order is in the list of order objects (dict), the entire request will raise an exception

        References:
            [API Docs](https://docs.bitpin.ir/v1/docs/order/Bulk%20Orders/Place_Bulk_Orders)

        Notes:
            Rate Limit: 1800 Requests/hour
        """

        max_orders = 10
        if len(orders) > max_orders:
            msg = "A maximum of 10 orders can be placed at a time! not creating order!"
            raise ValueError(msg)

        market = orders[0]["symbol"] if orders else None
        if any(order["symbol"] != market for order in orders):
            msg = "All orders must be in the same market! not creating order!"
            raise ValueError(msg)

        kwargs["json"] = {
            k: str(v)
            for k, v in locals().items()
            if v is not None and k not in {"self", "kwargs"}
        }
        return await self._post(self.BULK_ORDER_URL, signed=True, **kwargs)  # type: ignore[return-value]

    async def cancel_order_bulk(
        self,
        ids: t.OptionalStrList = None,
        identifiers: t.OptionalStrList = None,
        **kwargs,
    ) -> t.CancelBulkOrderResponse:
        """
        Cancel multiple orders in bulk using either order IDs or specific identifiers.

        Args:
            ids (Optional[List[str]]): A list of order IDs to cancel. Defaults to None.
            identifiers (Optional[List[str]]): A list of specific order identifiers to cancel. Defaults to None.
            **kwargs: Additional parameters.

        Returns:
            Response (dict): Response.

        References:
            [API Docs](https://docs.bitpin.ir/v1/docs/order/Bulk%20Orders/Cancel_Bulk_Orders)
        """

        kwargs["json"] = {
            k: str(v)
            for k, v in locals().items()
            if v is not None and k not in {"self", "kwargs"}
        }
        return await self._delete(self.BULK_ORDER_URL, signed=True, **kwargs)  # type: ignore[return-value]

    async def get_user_trades(  # type: ignore[no-untyped-def, override]
        self,
        symbol: t.OptionalStr = None,
        side: t.OptionalOrderTypesList = None,
        offset: t.OptionalInt = None,
        limit: t.OptionalInt = None,
        **kwargs,
    ) -> t.TradeResponse:
        """
        Retrieve user filled (executed) orders.

        Args:
            symbol (Optional[str]): symbol (e.g., BTC_IRT, ETH_USDT). Defaults to None.
            side (Optional[str]): The side of the trade, either 'buy' or 'sell'. Defaults to None.
            offset (Optional[int]): Fetch trades where the order ID is less than this value. Useful for pagination. Defaults to None.
            limit (Optional[int]): Maximum number of trades to retrieve, with an upper limit of 100. Defaults to None.
            **kwargs: Additional parameters.

        Returns:
            Response (dict): Response.

        References:
            [API Docs](https://docs.bitpin.ir/v1/docs/order/get_fills_list)

        Notes:
            Rate Limit: 80 Requests/minute
        """

        kwargs["params"] = kwargs.get("params", {})
        kwargs["params"].update(
            {
                k: str(v)
                for k, v in locals().items()
                if v is not None and k not in {"self", "kwargs"}
            }
        )

        return await self._get(self.ORDERS_URL, signed=True, **kwargs)  # type: ignore[return-value]

    async def close_connection(self) -> None:  # type: ignore[override]
        """Close connection."""

        await self.session.close()  # type: ignore[misc]
