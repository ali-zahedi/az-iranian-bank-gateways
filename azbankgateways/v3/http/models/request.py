from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from azbankgateways.v3.interfaces import HttpMethod, HttpRequestInterface


if TYPE_CHECKING:
    from azbankgateways.v3.http import URL


class HttpRequest(HttpRequestInterface):
    def __init__(
        self,
        http_method: HttpMethod,
        url: URL,
        timeout: int,
        headers: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> None:
        self._http_method = http_method
        self._url = url
        self._headers = headers or {}
        self._data = data or {}
        self._timeout = timeout

    @property
    def http_method(self) -> HttpMethod:
        return self._http_method

    @property
    def url(self) -> URL:
        return self._url

    @property
    def timeout(self) -> int:
        return self._timeout

    @property
    def headers(self) -> dict[str, Any]:
        return self._headers

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    @property
    def is_json(self) -> bool:
        return self.headers.get("Content-Type") == "application/json"
