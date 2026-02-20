from __future__ import annotations

import json
from importlib.resources import files
from typing import TYPE_CHECKING

import parametrize_from_file as pff
import requests


if TYPE_CHECKING:
    from responses import RequestsMock
    from syrupy.assertion import SnapshotAssertion

    from azbankgateways.v3.interfaces import (
        OrderDetails,
        ProviderConfigInterface,
        ProviderInterface,
    )
    from azbankgateways.v3.testing.syrupy.fixtures import ExceptionAssertion


TEST_DATA = json.load((files("tests.v3.providers") / "test_payment_request.json").open())


@pff.parametrize(
    schema=pff.defaults(**TEST_DATA["defaults"]["test_payment_request"])
)  # type: ignore[untyped-decorator]
def test_payment_request(
    provider_config_pair: tuple[ProviderInterface, ProviderConfigInterface],
    responses: RequestsMock,
    order_details: OrderDetails,
    provider_response: str | None,
    status_code: int,
    exception: str | None,
    capture_exception: ExceptionAssertion,
    snapshot: SnapshotAssertion,
) -> None:
    if not provider_response and not exception:
        raise NotImplementedError("Test case must define either 'provider_response' or 'exception'.")

    provider, config = provider_config_pair
    response_body = provider_response if exception is None else getattr(requests.exceptions, exception)()
    responses.add(
        method=responses.POST,
        url=str(config.payment_request_url),
        body=response_body,
        status=status_code,
        content_type="application/json",
    )

    with capture_exception():
        payment_request = provider.create_payment_request(order_details)

        assert str(payment_request.url) == snapshot(name="expected_url")
        assert payment_request.http_method.name == snapshot(name="expected_http_method")
        assert payment_request.data == snapshot(name="expected_http_data")
