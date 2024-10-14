from typing import Any, Dict

from azbankgateways.v3.interfaces import HttpMethod, RequestInterface


class RedirectRequest(RequestInterface):
    def __init__(
        self,
        http_method: HttpMethod,
        url: str,
        headers: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
        is_json: bool = False,
    ):
        self.__http_method = http_method
        self.__url = url
        self.__headers = headers if headers is not None else {}
        self.__data = data if data is not None else {}
        self.__is_json = is_json
        self.__validate_request()

    def __validate_request(self):
        if not self.__url:
            raise ValueError("URL cannot be empty.")
        if self.__http_method == HttpMethod.GET and self.__data:
            raise ValueError("GET requests should not have a body.")
        if self.__http_method not in set(HttpMethod):
            raise ValueError(f"Unsupported HTTP method: {self.__http_method}")

    @property
    def http_method(self) -> HttpMethod:
        return self.__http_method

    @property
    def url(self) -> str:
        return self.__url

    @property
    def headers(self) -> Dict[str, Any]:
        return self.__headers

    @property
    def data(self) -> Dict[str, Any]:
        return self.__data

    @property
    def is_json(self) -> bool:
        return self.__is_json
