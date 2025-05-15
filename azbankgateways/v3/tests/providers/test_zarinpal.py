from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from requests import ConnectionError
from requests import Timeout

from azbankgateways.exceptions.exceptions import BankGatewayConnectionError
from azbankgateways.exceptions.exceptions import BankGatewayRejectPayment
from azbankgateways.v3.currencies import CurrencyRegistry
from azbankgateways.v3.interfaces import OrderDetails
from azbankgateways.v3.providers.zarinpal import ZarinpalPaymentGatewayConfig
from azbankgateways.v3.providers.zarinpal import ZarinpalProvider

if TYPE_CHECKING:
    from typing import Any

    from responses import RequestsMock

    from azbankgateways.v3.interfaces import MessageServiceInterface


@pytest.fixture
def zarinpal_payment_config(currency_registry: Any, callback_url_generator: Any) -> ZarinpalPaymentGatewayConfig:
    return ZarinpalPaymentGatewayConfig(
        merchant_code="zarinpal-merchant-code",
        callback_url=callback_url_generator,
        payment_request_url="https://az.bank/request",
        start_payment_url="https://az.bank/start",
        currency=CurrencyRegistry.get_currency("IRT"),
    )


@pytest.fixture
def order_details() -> OrderDetails:
    return OrderDetails(
        amount=Decimal("1000.01"),
        tracking_code="tracking-code-1",
        first_name="John",
        last_name="Doe",
        phone_number="+989112223344",
        email="mail@az.bank",
        order_id="order-id",
        currency=CurrencyRegistry.get_currency("IRT").value,
    )


def test_zarinpal__payment_request__successful(
    responses: RequestsMock,
    zarinpal_payment_config: ZarinpalPaymentGatewayConfig,
    message_service: MessageServiceInterface,
    order_details: OrderDetails,
) -> None:
    provider = ZarinpalProvider(zarinpal_payment_config, message_service, order_details)

    responses.add(
        responses.POST,
        "https://az.bank/request",
        json={
            "data": {
                "code": 100,
                "message": "Success",
                "authority": "A0000000000000000000000000000wwOGYpd",
                "fee_type": "Merchant",
                "fee": 100,
            },
            "errors": [],
        },
        status=200,
    )

    assert provider.get_request_pay().url == "https://az.bank/start/A0000000000000000000000000000wwOGYpd"


@pytest.mark.parametrize(
    "errors",
    [  # noqa: PT007
        {
            "message": "The metadata.mobile must be a string.",
            "code": -9,
            "validations": [],
        },
        [
            {
                "message": "The metadata.mobile must be a string.",
                "code": -9,
                "validations": [],
            },
            {
                "message": "The metadata.order_id must be a string.",
                "code": -9,
                "validations": [],
            },
        ],
    ],
)
def test_zarinpal__payment_request__failed(
    responses: RequestsMock,
    zarinpal_payment_config: ZarinpalPaymentGatewayConfig,
    message_service: MessageServiceInterface,
    order_details: OrderDetails,
    errors: list[dict[str, Any]] | dict[str, Any],
) -> None:
    provider = ZarinpalProvider(zarinpal_payment_config, message_service, order_details)

    responses.add(
        responses.POST,
        "https://az.bank/request",
        json={"data": {}, "errors": errors},
        status=422,
    )

    with pytest.raises(BankGatewayRejectPayment):
        assert provider.get_request_pay()


@pytest.mark.parametrize(
    "side_effect",
    [  # noqa: PT007
        ConnectionError,
        Timeout,
    ],
)
def test_zarinpal__payment_request__failed__side_effect(
    responses: RequestsMock,
    zarinpal_payment_config: ZarinpalPaymentGatewayConfig,
    message_service: MessageServiceInterface,
    order_details: OrderDetails,
    side_effect: Any,
) -> None:
    provider = ZarinpalProvider(zarinpal_payment_config, message_service, order_details)

    responses.add(
        responses.POST,
        "https://az.bank/request",
        body=side_effect(),
    )

    with pytest.raises(BankGatewayConnectionError):
        assert provider.get_request_pay()


def test_zarinpal__minimum_amount(
    zarinpal_payment_config: ZarinpalPaymentGatewayConfig,
    message_service: MessageServiceInterface,
    order_details: OrderDetails,
) -> None:
    order_details.amount = Decimal(100)
    provider = ZarinpalProvider(zarinpal_payment_config, message_service, order_details)

    with pytest.raises(BankGatewayRejectPayment):
        assert provider.get_request_pay()
