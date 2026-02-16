from __future__ import annotations

from typing import TYPE_CHECKING, Generator

import pytest
import responses as responses_lib

from azbankgateways.v3.http import HTTPClient, HTTPRequest, HTTPResponse
from azbankgateways.v3.http.models.headers import HTTPHeaders
from azbankgateways.v3.message_services import MessageService


if TYPE_CHECKING:
    from azbankgateways.v3.interfaces import (
        HTTPClientInterface,
        HTTPHeadersInterface,
        HTTPRequestInterface,
        HTTPResponseInterface,
        MessageServiceInterface,
    )

pytest_plugins = ("azbankgateways.v3.testing.syrupy.fixtures",)


@pytest.fixture(autouse=True)
def responses() -> Generator[responses_lib.RequestsMock, responses_lib.RequestsMock, None]:
    """
    Globally register responses in every test.
    This causes every test to fail that makes external HTTP requests via the "requests" library.
    If a test does this, it is required to explicitly define a mock response by using this fixture.
    This is intentionally: Sometimes, tests make external requests without being aware. If the external API is
    not responding, it causes flaky tests. So we would rather know about those API usages right when writing new tests.

    In comparison to using "import responses", we also get the benefit of responses notifying us when mocked
    responses *are not* used in a test. This is useful to ensure that the test is actually using the mocked response.

    See: https://github.com/getsentry/responses?tab=readme-ov-file#responses-as-a-pytest-fixture
    """
    with responses_lib.RequestsMock() as requests_mock:
        yield requests_mock


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
def http_client(
    http_response_class: type[HTTPResponseInterface], http_headers_class: type[HTTPHeadersInterface]
) -> HTTPClientInterface:
    return HTTPClient(http_response_class, http_headers_class)


@pytest.fixture(scope="session")
def message_service() -> MessageServiceInterface:
    return MessageService()
