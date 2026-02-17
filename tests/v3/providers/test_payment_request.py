from __future__ import annotations

import json
from importlib.resources import files
from typing import TYPE_CHECKING, Any, Callable

import parametrize_from_file as pff
import requests


if TYPE_CHECKING:
    from responses import RequestsMock

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
    provider_config_pairs: list[tuple[ProviderInterface, ProviderConfigInterface]],
    responses: RequestsMock,
    order_details: OrderDetails,
    load_provider_response: Callable[[ProviderInterface, str], dict[str, Any]],
    status_code: int,
    exception: str | None,
    response_fixture: str | None,
    expected_token: str | None,
    capture_exception: ExceptionAssertion,
) -> None:
    for provider, config in provider_config_pairs:
        json_response = (
            json.dumps(load_provider_response(provider, response_fixture)) if response_fixture else None
        )
        payment_request_url = getattr(config, 'payment_request_url', None)
        if not payment_request_url:
            raise NotImplementedError(
                f"Provider '{provider.name}' configuration does not define 'payment_request_url'."
            )
        responses.add(
            method=responses.POST,
            url=str(payment_request_url),
            body=json_response if exception is None else getattr(requests.exceptions, exception)(),
            status=status_code,
            content_type="application/json",
        )

        with capture_exception():
            payment_request = provider.create_payment_request(order_details)

            if expected_token is not None:
                assert expected_token in str(payment_request.url)
