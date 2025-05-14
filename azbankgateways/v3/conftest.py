from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import responses as responses_lib

from azbankgateways.v3.currencies import CurrencyRegistry
from azbankgateways.v3.interfaces import Currency
from azbankgateways.v3.message_services import MessageService

if TYPE_CHECKING:
    from collections.abc import Generator

    from azbankgateways.v3.interfaces import CallbackURLType
    from azbankgateways.v3.interfaces import MessageServiceInterface
    from azbankgateways.v3.interfaces import OrderDetails


@pytest.fixture(autouse=True)
def responses() -> Generator[responses_lib.RequestsMock]:
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
    with responses_lib.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def currency_registry() -> type[CurrencyRegistry]:
    CurrencyRegistry.register_currency(Currency.IRR)
    CurrencyRegistry.register_currency(Currency.IRT)
    return CurrencyRegistry


@pytest.fixture
def message_service() -> MessageServiceInterface:
    return MessageService()


@pytest.fixture
def base_callback_url() -> str:
    return "https://az.bank/callback"


@pytest.fixture
def callback_url_generator(base_callback_url: str) -> CallbackURLType:
    def callback(order_details: OrderDetails) -> str:
        return f"{base_callback_url}/{order_details.tracking_code}"

    return callback
