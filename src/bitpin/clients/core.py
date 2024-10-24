"""# Core Client."""

import os
from abc import (
    ABC,
    abstractmethod,
)

from .. import response_types as t


class CoreClient(ABC):  # pylint: disable=too-many-instance-attributes
    """Core Client."""

    API_URL = "https://api.bitpin.ir/api"

    PUBLIC_API_VERSION_1 = "v1"
    PUBLIC_API_VERSION_2 = "v2"

    REQUEST_TIMEOUT: float = 10

    LOGIN_URL = "usr/authenticate/"
    REFRESH_TOKEN_URL = "usr/refresh_token/"
    CURRENCIES_LIST_URL = "mkt/currencies/"
    MARKETS_LIST_URL = "mkt/markets/"
    TICKERS_LIST_URL = "mkt/tickers/"
    WALLETS_URL = "wlt/wallets/"
    ORDERBOOK_URL = "mth/orderbook/{}/"
    RECENT_TRADES_URL = "mth/matches/{}/"
    ORDERS_URL = "odr/orders/"
    FILLED_ORDERS_URL = "odr/fills/"
    USER_TRADES_URL = "odr/matches/?type={}"
    BULK_ORDER_URL = "odr/orders/bulk/"

    def __init__(  # type: ignore[no-untyped-def]
        self,
        api_key: t.OptionalStr = None,
        api_secret: t.OptionalStr = None,
        access_token: t.OptionalStr = None,
        refresh_token: t.OptionalStr = None,
        requests_params: t.OptionalDictStrAny = None,
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

            If `requests_params` are provided in method's `kwargs`, they will override existing `requests_params`.

            If `background_relogin` is enabled, access token will be refreshed in background every
            `background_relogin_interval` seconds.

            If `background_refresh_token` is enabled, refresh token will be refreshed in background every
            `background_refresh_token_interval` seconds.
        """

        self.api_key = api_key or os.environ.get("BITPIN_API_KEY")
        self.api_secret = api_secret or os.environ.get("BITPIN_API_SECRET")
        self.access_token: t.OptionalStr = access_token or os.environ.get("BITPIN_ACCESS_TOKEN")
        self.refresh_token: t.OptionalStr = refresh_token or os.environ.get("BITPIN_REFRESH_TOKEN")

        self._background_relogin = background_relogin
        self._background_relogin_interval = background_relogin_interval
        self._background_refresh_token = background_refresh_token
        self._background_refresh_token_interval = background_refresh_token_interval

        self._requests_params = requests_params
        self.session = self._init_session()

    def _get_request_kwargs(
        self, method: t.RequestMethods, signed: bool, **kwargs
    ) -> t.DictStrAny:  # type: ignore[no-untyped-def]
        kwargs["timeout"] = self.REQUEST_TIMEOUT

        if self._requests_params:
            kwargs.update(self._requests_params)

        data = kwargs.get("data")
        if data and isinstance(data, dict):
            kwargs["data"] = data

            if "requests_params" in kwargs["data"]:
                kwargs.update(kwargs["data"]["requests_params"])
                del kwargs["data"]["requests_params"]

        if signed is True:
            headers: t.DictStrAny = kwargs.get("headers", {})
            headers.update({"Authorization": f"Bearer {self.access_token}"})
            kwargs["headers"] = headers

        if data and method == "get":
            kwargs["params"] = "&".join(f"{data[0]}={data[1]}" for data in kwargs["data"])
            del kwargs["data"]

        return kwargs

    @staticmethod
    def _pick(response: t.DictStrAny, key: str, value: t.t.Any, result_key: str = "results") -> t.DictStrAny:
        for _ in response.get(result_key, []):
            if _[key] == value:
                response[result_key] = _
                return response
        raise ValueError(f"{key} {value} not found in {response}")

    def _create_api_uri(self, path: str, version: str = PUBLIC_API_VERSION_1) -> str:
        return self.API_URL + "/" + str(version) + "/" + path

    @abstractmethod
    def _init_session(self) -> t.HttpSession:
        """
        Initialize session.

        Returns:
            session (t.Union[requests.Session, aiohttp.ClientSession]): Session.
        """

        raise NotImplementedError

    @abstractmethod
    def _get(
        self,
        path: str,
        signed: bool = False,
        version: str = PUBLIC_API_VERSION_1,
        **kwargs,
    ) -> t.DictStrAny:  # type: ignore[no-untyped-def]
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

        raise NotImplementedError

    @abstractmethod
    def _post(
        self,
        path: str,
        signed: bool = False,
        version: str = PUBLIC_API_VERSION_1,
        **kwargs,
    ) -> t.DictStrAny:  # type: ignore[no-untyped-def]
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

        raise NotImplementedError

    @abstractmethod
    def _delete(
        self,
        path: str,
        signed: bool = False,
        version: str = PUBLIC_API_VERSION_1,
        **kwargs,
    ) -> t.DictStrAny:  # type: ignore[no-untyped-def]
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

        raise NotImplementedError

    @abstractmethod
    def _request_api(  # type: ignore[no-untyped-def]
        self,
        method: t.RequestMethods,
        path: str,
        signed: bool = False,
        version: str = PUBLIC_API_VERSION_1,
        **kwargs,
    ) -> t.DictStrAny:
        """
        Request API.

        Args:
            method (str): Method (GET, POST, PUT, DELETE).
            path (str): Path.
            signed (bool): Signed.
            version (str): Version.
            **kwargs: Kwargs.

        Returns:
            dict: Response.
        """

        raise NotImplementedError

    @abstractmethod
    def _request(
        self, method: t.RequestMethods, uri: str, signed: bool, **kwargs
    ) -> t.DictStrAny:  # type: ignore[no-untyped-def]
        """
        Request.

        Args:
            method (str): Method (GET, POST, PUT, DELETE).
            uri (str): URI.
            signed (bool): Signed.
            **kwargs: Kwargs.

        Returns:
            dict: Response.
        """

        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _handle_response(response: t.HttpResponses) -> t.DictStrAny:
        """
        Handle response.

        Args:
            response (t.Union[requests.Response, aiohttp.ClientResponse]): Response.

        Returns:
            dict: Response.
        """

        raise NotImplementedError

    @abstractmethod
    def _handle_login(self) -> None:
        """Handle login."""

        raise NotImplementedError

    @abstractmethod
    def _background_relogin_task(self) -> None:
        """Background relogin task."""

        raise NotImplementedError

    @abstractmethod
    def _background_refresh_token_task(self) -> None:
        """Background refresh token task."""

        raise NotImplementedError

    @abstractmethod
    def login(self, **kwargs) -> t.LoginResponse:  # type: ignore[no-untyped-def]
        """
        Login.

        Returns:
            dict: Response.
        """

        raise NotImplementedError

    @abstractmethod
    def refresh_access_token(
        self, refresh_token: t.OptionalStr = None, **kwargs
    ) -> t.RefreshTokenResponse:  # type: ignore[no-untyped-def]
        """
        Refresh token.

        Args:
            refresh_token (str): Refresh token.

        Returns:
            dict: Response.
        """

        raise NotImplementedError

    @abstractmethod
    def get_user_info(self, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """
        Get user info. (Deprecated)

        Returns:
            None.
        """

        raise NotImplementedError

    @abstractmethod
    def get_currencies_info(self) -> t.CurrenciesInfo:  # type: ignore[no-untyped-def]
        """
        Get currencies info.

        Returns:
            dict: Response.
        """

        raise NotImplementedError

    @abstractmethod
    def get_markets_info(self) -> t.MarketsInfo:  # type: ignore[no-untyped-def]
        """
        Get markets info.

        Returns:
            dict: Response.
        """

        raise NotImplementedError

    @abstractmethod
    def get_tickers_info(self) -> t.DictStrAny:  # type: ignore[no-untyped-def]
        """
        Get tickers info.

        Returns:
            dict: Response.
        """

        raise NotImplementedError

    @abstractmethod
    def get_wallets(
        self,
        assets: t.OptionalStr,
        service: t.OptionalStr,
        offset: t.OptionalFloat,
        limit: t.OptionalInt,
    ) -> t.DictStrAny:  # type: ignore[no-untyped-def]
        """
        Get wallets.

        Args:
            assets: asset name [BTC, IRT, USDT, ...]
            service: name of service
            offset: asset balance offset, i.e. assets below 10000
            limit: maximum received assets info

        Returns:
            Response (dict): Response.

        Notes:
            Rate limit: 10000/day.
        """

        raise NotImplementedError

    @abstractmethod
    def get_orderbook(
        self,
        symbol: str,
    ) -> t.OrderbookResponse:  # type: ignore[no-untyped-def]  # pylint: disable=redefined-builtin
        """
        Get orderbook.

        Args:
            symbol (str): i.e. BTC_IRT, ETH_USDT

        Returns:
            Response (dict): Response.
        """

        raise NotImplementedError

    @abstractmethod
    def get_recent_trades(self, symbol: str) -> t.RecentTradesInfo:
        """
        Get recent trades.

        Args:
            symbol (str): i.e. BTC_IRT.

        Returns:
            Response (dict): Response.
        """

        raise NotImplementedError

    @abstractmethod
    def get_user_orders(  # type: ignore[no-untyped-def]
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
        """

        raise NotImplementedError

    @abstractmethod
    def create_order(  # type: ignore[no-untyped-def]
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
        """

        raise NotImplementedError

    @abstractmethod
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
        """

        raise NotImplementedError

    @abstractmethod
    def cancel_order_bulk(
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
            t.CancelBulkOrderResponse
        """

        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, order_id: str, **kwargs) -> t.CancelOrderResponse:  # type: ignore[no-untyped-def]
        """
        Cancel order.

        Args:
            order_id (str): Order ID.

        Returns:
            dict: Response.
        """

        raise NotImplementedError

    @abstractmethod
    def get_user_trades(  # type: ignore[no-untyped-def]
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
        """

        raise NotImplementedError

    @abstractmethod
    def close_connection(self) -> None:
        """Close connection."""

        raise NotImplementedError
