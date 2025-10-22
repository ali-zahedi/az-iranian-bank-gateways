from typing import Any, Dict, Optional, Self

from azbankgateways.v3.http_utils import URL
from azbankgateways.v3.interfaces import HttpMethod, HttpRequestInterface


class RedirectRequest(HttpRequestInterface):
    def __init__(
        self,
        http_method: HttpMethod,
        url: URL,
        timeout: int = 20,
        headers: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
    ):
        if not self.__allow_init:
            raise RuntimeError("Direct instantiation is not allowed. Use RedirectRequest.create(...)")

        self.__http_method = http_method
        self.__url = url
        self.__headers = headers if headers is not None else {}
        self.__data = data if data is not None else {}
        self.__timeout = timeout
        self.__validate_request()

    @classmethod
    def create(
        cls,
        http_method: HttpMethod,
        url: URL,
        timeout: int = 20,
        headers: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> Self:
        obj = cls.__new__(cls)
        obj.__allow_init = True
        obj.__init__(http_method, url, timeout, headers, data)
        obj.__allow_init = False
        return obj

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
    def url(self) -> URL:
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

    @property
    def timeout(self) -> int:
        return self.__timeout
