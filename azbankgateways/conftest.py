from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from azbankgateways.v3.http import HTTPClient, HTTPRequest, HTTPResponse
from azbankgateways.v3.http.models.headers import HTTPHeaders


if TYPE_CHECKING:
    from azbankgateways.v3.interfaces import (
        HTTPHeadersInterface,
        HTTPRequestInterface,
        HTTPResponseInterface,
    )


@pytest.fixture
def http_request_class() -> type[HTTPRequestInterface]:
    return HTTPRequest


@pytest.fixture
def http_response_class() -> type[HTTPResponseInterface]:
    return HTTPResponse


@pytest.fixture
def http_headers_class() -> type[HTTPHeadersInterface]:
    return HTTPHeaders


@pytest.fixture
def http_client(http_response_class: type[HTTPResponse], http_headers_class: type[HTTPHeaders]) -> HTTPClient:
    return HTTPClient(http_response_class, http_headers_class)
