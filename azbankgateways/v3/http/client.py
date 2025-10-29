from __future__ import annotations

import json
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Type, TypeVar

import requests

from azbankgateways.v3.exceptions.internal import InternalConnectionError
from azbankgateways.v3.interfaces import HttpClientInterface


if TYPE_CHECKING:
    from azbankgateways.v3.http import HttpRequest, HttpResponse


T = TypeVar("T", bound="HttpClientInterface")


class HttpClientMeta(ABCMeta):
    def __call__(cls: Type[T], http_response_cls: Type[HttpResponse]) -> T:
        return super().__call__(http_response_cls=http_response_cls)


class HttpClient(HttpClientInterface, metaclass=HttpClientMeta):
    def __init__(self, http_response_cls: type[HttpResponse]) -> None:
        self.http_response_cls = http_response_cls

    @abstractmethod
    def send(self, request: HttpRequest) -> HttpResponse:
        raise NotImplementedError("Subclasses must implement the `send` method.")


class DefaultHttpClient(HttpClient):
    def send(self, request: HttpRequest) -> HttpResponse:
        data = json.dumps(request.data) if request.is_json else request.data

        try:
            response = requests.request(
                request.http_method.value,
                str(request.url),
                data=data,
                headers=request.headers,
                timeout=request.timeout,
            )
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.RequestException,
        ) as e:
            raise InternalConnectionError(request, exception=e) from e
        return self.http_response_cls(
            status_code=response.status_code,
            headers=response.headers,
            body=response.content,
        )
