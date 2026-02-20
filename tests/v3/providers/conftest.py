from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from azbankgateways.v3.http import HTTPClient
from azbankgateways.v3.interfaces import OrderDetails
from tests.v3.providers.utils import (
    discover_provider_classes,
    get_provider_config_factory_pairs,
)


if TYPE_CHECKING:
    from azbankgateways.v3.interfaces import (
        HTTPHeadersInterface,
        HTTPRequestInterface,
        ProviderConfigInterface,
        ProviderInterface,
    )
    from azbankgateways.v3.message_services import MessageService


@pytest.fixture(scope="session")
def provider_classes() -> list[type[ProviderInterface]]:
    return discover_provider_classes()


@pytest.fixture
def provider_response(
    request: pytest.FixtureRequest, provider_config_pair: tuple[ProviderInterface, ProviderConfigInterface]
) -> str | None:
    """
    Fixture to load a provider response JSON file dynamically.
    """

    provider, config = provider_config_pair
    provider_name = provider.name.name.lower()
    test_id = request.node.callspec.id.replace(f'{provider_name}-', '')
    path = Path("tests/v3/providers/responses") / provider_name / f"{test_id}.json"
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return f.read()


# TODO: Refactor this fixture to avoid hardcoded static values.
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


@pytest.fixture(
    params=get_provider_config_factory_pairs(),
    ids=lambda pair: pair[0].__name__.replace("Provider", "").lower(),
)
def provider_config_pair(
    request: pytest.FixtureRequest,
    message_service: MessageService,
    http_client: HTTPClient,
    http_request_class: type[HTTPRequestInterface],
    http_headers_class: type[HTTPHeadersInterface],
) -> tuple[ProviderInterface, ProviderConfigInterface]:
    provider_class, provider_config_factory_class = request.param
    config = provider_config_factory_class()
    provider = provider_class(
        config=config,
        message_service=message_service,
        http_client=http_client,
        http_request_class=http_request_class,
        http_headers_class=http_headers_class,
    )
    return provider, config
