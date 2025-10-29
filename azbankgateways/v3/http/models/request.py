from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Optional, Type, TypeVar

from azbankgateways.v3.interfaces import HttpMethod, HttpRequestInterface


if TYPE_CHECKING:
    from azbankgateways.v3.http import URL

T = TypeVar("T", bound="HttpRequestInterface")


class HttpRequestMeta(ABCMeta):
    def __call__(
        cls: Type[T],
        http_method: HttpMethod,
        url: URL,
        timeout: int,
        headers: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> T:
        return super().__call__(http_method=http_method, url=url, timeout=timeout, headers=headers, data=data)


class HttpRequest(HttpRequestInterface, metaclass=HttpRequestMeta):
    def __init__(
        self,
        http_method: HttpMethod,
        url: URL,
        timeout: int,
        headers: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> None:
        self.http_method = http_method
        self.url = url
        self.headers = headers or {}
        self.data = data or {}
        self.timeout = timeout

    @property
    @abstractmethod
    def is_json(self) -> bool:
        raise NotImplementedError("Subclasses must implement the `is_json` property.")


class DefaultHttpRequest(HttpRequest):
    @property
    def is_json(self) -> bool:
        return self.headers.get("Content-Type") == "application/json"
