from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Generator, cast

import pytest
import responses as responses_lib

from azbankgateways.v3.http import HTTPClient, HTTPRequest, HTTPResponse
from azbankgateways.v3.http.models.headers import HTTPHeaders
from azbankgateways.v3.interfaces import OrderDetails
from azbankgateways.v3.message_services import MessageService


if TYPE_CHECKING:
    from azbankgateways.v3.interfaces import (
        HTTPClientInterface,
        HTTPHeadersInterface,
        HTTPRequestInterface,
        HTTPResponseInterface,
        MessageServiceInterface,
        ProviderInterface,
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


@pytest.fixture(scope="session")
def http_request_class() -> type[HTTPRequestInterface]:
    return HTTPRequest


@pytest.fixture(scope="session")
def http_response_class() -> type[HTTPResponseInterface]:
    return HTTPResponse


@pytest.fixture(scope="session")
def http_headers_class() -> type[HTTPHeadersInterface]:
    return HTTPHeaders


@pytest.fixture(scope="session")
def http_client(
    http_response_class: type[HTTPResponseInterface], http_headers_class: type[HTTPHeadersInterface]
) -> HTTPClientInterface:
    return HTTPClient(http_response_class, http_headers_class)


@pytest.fixture(scope="session")
def message_service() -> MessageServiceInterface:
    return MessageService()


@pytest.fixture
def order_details() -> OrderDetails:
    return OrderDetails(
        amount=Decimal(1000.01),
        tracking_code="tracking-code-1",
        first_name='John',
        last_name='Doe',
        phone_number='+989112223344',
        email='mail@az.bank',
        order_id='order-id',
    )


@pytest.fixture(scope="session")
def load_provider_response() -> Callable[[ProviderInterface, str], dict[str, Any]]:
    """
    Fixture to load a provider response JSON file dynamically.
    Usage in a test: `load_provider_response(provider)`
    """

    def _loader(provider: ProviderInterface, response_fixture: str) -> dict[str, Any]:
        provider_name = provider.name.name.lower()
        path = Path("tests/v3/providers/responses") / provider_name / f"{response_fixture}.json"

        if not path.exists():
            raise FileNotFoundError(f"Response file not found: {path}")

        with path.open("r", encoding="utf-8") as f:
            return cast(dict[str, Any], json.load(f))

    return _loader
