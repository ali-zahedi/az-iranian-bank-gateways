from __future__ import annotations

from typing import TYPE_CHECKING

import responses as responses_lib
from pytest import fixture

from azbankgateways.v3.http import URL
from azbankgateways.v3.message_services import MessageService


if TYPE_CHECKING:
    from typing import Any

    from azbankgateways.v3.interfaces import MessageServiceInterface, OrderDetails
    from azbankgateways.v3.typing import CallbackURL


@fixture(autouse=True)
def responses() -> Any:
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


@fixture
def message_service() -> MessageServiceInterface:
    return MessageService()


@fixture
def base_callback_url() -> str:
    return 'https://az.bank/callback'


@fixture
def callback_url_generator(base_callback_url: str) -> CallbackURL:
    def callback(order_details: OrderDetails) -> URL:
        return URL(base_callback_url).join(order_details.tracking_code)

    return callback
