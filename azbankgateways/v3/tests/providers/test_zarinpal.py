from decimal import Decimal

import pytest
from requests import ConnectionError, Timeout

from azbankgateways.exceptions.exceptions import (
    BankGatewayConnectionError,
    BankGatewayRejectPayment,
)
from azbankgateways.v3.currencies import CurrencyRegistry
from azbankgateways.v3.interfaces import OrderDetails
from azbankgateways.v3.providers.zarinpal import (
    ZarinpalPaymentGatewayConfig,
    ZarinpalProvider,
)


@pytest.fixture
def zarinpal_payment_config(currency_registry, callback_url_generator):
    return ZarinpalPaymentGatewayConfig(
        merchant_code="zarinpal-merchant-code",
        callback_url=callback_url_generator,
        payment_request_url="https://az.bank/request",
        start_payment_url="https://az.bank/start",
        currency=CurrencyRegistry.get_currency("IRT"),
    )


@pytest.fixture
def order_details():
    return OrderDetails(
        amount=Decimal(1000.01),
        tracking_code="tracking-code-1",
        first_name='John',
        last_name='Doe',
        phone_number='+989112223344',
        email='mail@az.bank',
        order_id='order-id',
        currency=CurrencyRegistry.get_currency("IRT").value,
    )


def test_zarinpal__payment_request__successful(
    responses, zarinpal_payment_config, message_service, order_details
):
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

    assert provider.get_request_pay().url == 'https://az.bank/start/A0000000000000000000000000000wwOGYpd'


@pytest.mark.parametrize(
    "errors",
    [
        {"message": "The metadata.mobile must be a string.", "code": -9, "validations": []},
        [
            {"message": "The metadata.mobile must be a string.", "code": -9, "validations": []},
            {"message": "The metadata.order_id must be a string.", "code": -9, "validations": []},
        ],
    ],
)
def test_zarinpal__payment_request__failed(
    responses, zarinpal_payment_config, message_service, order_details, errors
):
    provider = ZarinpalProvider(zarinpal_payment_config, message_service, order_details)

    responses.add(
        responses.POST,
        "https://az.bank/request",
        json={"data": {}, "errors": errors},
        status=422,
    )

    with pytest.raises(BankGatewayRejectPayment):
        assert provider.get_request_pay()


@pytest.mark.parametrize("side_effect", [ConnectionError, Timeout])
def test_zarinpal__payment_request__failed__side_effect(
    responses, zarinpal_payment_config, message_service, order_details, side_effect
):
    provider = ZarinpalProvider(zarinpal_payment_config, message_service, order_details)

    responses.add(
        responses.POST,
        "https://az.bank/request",
        body=side_effect(),
    )

    with pytest.raises(BankGatewayConnectionError):
        assert provider.get_request_pay()


def test_zarinpal__minimum_amount(zarinpal_payment_config, message_service, order_details):
    order_details.amount = Decimal(100)
    provider = ZarinpalProvider(zarinpal_payment_config, message_service, order_details)

    with pytest.raises(BankGatewayRejectPayment):
        assert provider.get_request_pay()
