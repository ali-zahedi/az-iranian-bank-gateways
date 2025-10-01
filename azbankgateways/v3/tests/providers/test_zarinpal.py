from decimal import Decimal

import pytest
from requests import ConnectionError, Timeout

from azbankgateways.v3.exceptions.internal import (
    BankGatewayConnectionError,
    BankGatewayMinimumAmountError,
    BankGatewayRejectPayment,
)
from azbankgateways.v3.http_utils import URL
from azbankgateways.v3.interfaces import OrderDetails
from azbankgateways.v3.providers.zarinpal import (
    ZarinpalPaymentGatewayConfig,
    ZarinpalProvider,
)


@pytest.fixture
def zarinpal_payment_config(callback_url_generator):
    return ZarinpalPaymentGatewayConfig(
        merchant_code="zarinpal-merchant-code",
        callback_url_generator=callback_url_generator,
        payment_request_url=URL("https://az.bank/request/"),
        start_payment_url=URL("https://az.bank/start/"),
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
    )


def test_zarinpal__payment_request__successful(
    responses, zarinpal_payment_config, message_service, order_details, http_client, http_request_cls
):
    provider = ZarinpalProvider.create(
        zarinpal_payment_config, message_service, http_client, http_request_cls
    )
    responses.add(
        responses.POST,
        "https://az.bank/request/",
        json={
            "data": {
                "code": 100,
                "message": "Success",
                "authority": "A00000001",
                "fee_type": "Merchant",
                "fee": 100,
            },
            "errors": [],
        },
        status=200,
    )

    payment_request = provider.create_payment_request(order_details)

    assert str(payment_request.url) == 'https://az.bank/start/A00000001'


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
    responses,
    zarinpal_payment_config,
    message_service,
    order_details,
    errors,
    http_client,
    http_request_cls,
):
    provider = ZarinpalProvider.create(
        zarinpal_payment_config, message_service, http_client, http_request_cls
    )
    responses.add(
        responses.POST,
        "https://az.bank/request/",
        json={"data": {}, "errors": errors},
        status=422,
    )

    with pytest.raises(BankGatewayRejectPayment):
        assert provider.create_payment_request(order_details)


@pytest.mark.parametrize("side_effect", [ConnectionError, Timeout])
def test_zarinpal__payment_request__failed__side_effect(
    responses,
    zarinpal_payment_config,
    message_service,
    order_details,
    side_effect,
    http_client,
    http_request_cls,
):
    provider = ZarinpalProvider.create(
        zarinpal_payment_config, message_service, http_client, http_request_cls
    )
    responses.add(
        responses.POST,
        "https://az.bank/request/",
        body=side_effect(),
    )

    with pytest.raises(BankGatewayConnectionError):
        assert provider.create_payment_request(order_details)


def test_zarinpal__minimum_amount(
    zarinpal_payment_config, message_service, order_details, http_client, http_request_cls
):
    order_details.amount = Decimal(100)
    provider = ZarinpalProvider.create(
        zarinpal_payment_config, message_service, http_client, http_request_cls
    )

    with pytest.raises(BankGatewayMinimumAmountError):
        assert provider.create_payment_request(order_details)
