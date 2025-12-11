from __future__ import annotations

import json
from typing import TYPE_CHECKING

import requests

from azbankgateways.v3.exceptions.internal import InternalConnectionError
from azbankgateways.v3.interfaces import HttpClientInterface, HttpHeadersInterface


if TYPE_CHECKING:
    from azbankgateways.v3.interfaces import HttpRequestInterface, HttpResponseInterface


class HttpClient(HttpClientInterface):
    def __init__(
        self, http_response_class: type[HttpResponseInterface], http_headers_class: type[HttpHeadersInterface]
    ) -> None:
        self._http_response_class = http_response_class
        self._http_headers_class = http_headers_class

    @property
    def http_response_class(self) -> type[HttpResponseInterface]:
        return self._http_response_class

    def send(self, request: HttpRequestInterface) -> HttpResponseInterface:
        data = json.dumps(request.data) if request.is_json else request.data

        try:
            response = requests.request(
                request.http_method.value,
                str(request.url),
                data=data,
                headers=request.headers.to_dict(),
                timeout=request.timeout,
            )
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.RequestException,
        ) as e:
            raise InternalConnectionError(request, exception=e) from e
        return self.http_response_class(
            status_code=response.status_code,
            headers=self._http_headers_class(response.headers),
            body=response.content,
        )
