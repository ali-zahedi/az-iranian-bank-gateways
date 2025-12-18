from __future__ import annotations

import json
from typing import TYPE_CHECKING

import requests

from azbankgateways.v3.exceptions.internal import InternalConnectionError
from azbankgateways.v3.interfaces import HTTPClientInterface


if TYPE_CHECKING:
    from azbankgateways.v3.interfaces import (
        HTTPHeadersInterface,
        HTTPRequestInterface,
        HTTPResponseInterface,
    )


class HTTPClient(HTTPClientInterface):
    def __init__(
        self, http_response_class: type[HTTPResponseInterface], http_headers_class: type[HTTPHeadersInterface]
    ) -> None:
        self._http_response_class = http_response_class
        self._http_headers_class = http_headers_class

    @property
    def http_response_class(self) -> type[HTTPResponseInterface]:
        return self._http_response_class

    def send(self, request: HTTPRequestInterface) -> HTTPResponseInterface:
        data = json.dumps(request.data) if request.is_json else request.data

        try:
            response = requests.request(
                request.http_method.value,
                str(request.url),
                data=data,
                headers=request.headers.to_dict() if request.headers else None,
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
            headers=self._http_headers_class(dict(response.headers)),
            body=response.content,
        )
