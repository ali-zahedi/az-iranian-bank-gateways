from __future__ import annotations

from typing import TYPE_CHECKING, Any

from azbankgateways.v3.interfaces import HTTPRequestInterface


if TYPE_CHECKING:
    from azbankgateways.v3.http import URL
    from azbankgateways.v3.interfaces import HTTPHeadersInterface, HTTPMethod


class HTTPRequest(HTTPRequestInterface):
    def __init__(
        self,
        http_method: HTTPMethod,
        url: URL,
        timeout: int,
        headers: HTTPHeadersInterface | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        self._http_method = http_method
        self._url = url
        self._headers = headers
        self._data = data or {}
        self._timeout = timeout

    @property
    def http_method(self) -> HTTPMethod:
        return self._http_method

    @property
    def url(self) -> URL:
        return self._url

    @property
    def timeout(self) -> int:
        return self._timeout

    @property
    def headers(self) -> HTTPHeadersInterface | None:
        return self._headers

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    @property
    def is_json(self) -> bool:
        return self.headers.is_json if self.headers else False
