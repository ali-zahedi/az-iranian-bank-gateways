from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from requests import ConnectionError, Timeout

from azbankgateways.v3.exceptions.internal import (
    InternalConnectionError,
    InternalInvalidGatewayResponseError,
    InternalMinimumAmountError,
    InternalRejectPaymentError,
)
from azbankgateways.v3.http import URL
from azbankgateways.v3.interfaces import OrderDetails, PaymentStatus
from azbankgateways.v3.message_services import MessageService
from azbankgateways.v3.providers.zarinpal import (
    ZarinpalPaymentGatewayConfig,
    ZarinpalProvider,
)


if TYPE_CHECKING:
    from responses import RequestsMock

    from azbankgateways.v3.interfaces import (
        HTTPClientInterface,
        HTTPHeadersInterface,
        HTTPRequestInterface,
    )
    from azbankgateways.v3.typing import CallbackURL, JSONDocument


@pytest.fixture
def zarinpal_payment_config(callback_url_generator: CallbackURL) -> ZarinpalPaymentGatewayConfig:
    return ZarinpalPaymentGatewayConfig(
        merchant_code="zarinpal-merchant-code",
        callback_url_generator=callback_url_generator,
        payment_request_url=URL("https://az.bank/request/"),
        start_payment_url=URL("https://az.bank/start/"),
        verify_payment_url=URL("https://az.bank/verify/"),
        reverse_payment_url=URL("https://az.bank/reverse/"),
        inquiry_payment_url=URL("https://az.bank/inquiry/"),
    )


@pytest.fixture
def zarinpal_provider(
    zarinpal_payment_config: ZarinpalPaymentGatewayConfig,
    message_service: MessageService,
    http_client: HTTPClientInterface,
    http_request_class: type[HTTPRequestInterface],
    http_headers_class: type[HTTPHeadersInterface],
) -> ZarinpalProvider:
    """Fixture to create a ZarinpalProvider instance."""
    return ZarinpalProvider(
        zarinpal_payment_config,
        message_service,
        http_client,
        http_request_class,
        http_headers_class,
    )


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


def test_zarinpal_payment_request__successful(
    zarinpal_provider: ZarinpalProvider,
    responses: RequestsMock,
    order_details: OrderDetails,
) -> None:
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

    payment_request = zarinpal_provider.create_payment_request(order_details)

    assert str(payment_request.url) == 'https://az.bank/start/A00000001/'


def test_zarinpal_payment_request__invalid_gateway_response(
    zarinpal_provider: ZarinpalProvider,
    responses: RequestsMock,
    order_details: OrderDetails,
) -> None:
    responses.add(
        responses.POST,
        "https://az.bank/request/",
        json={
            "data": {
                "code": 100,
                "message": "Success",
                "fee_type": "Merchant",
                "fee": 100,
            },
            "errors": [],
        },
        status=200,
    )

    with pytest.raises(InternalInvalidGatewayResponseError):
        zarinpal_provider.create_payment_request(order_details)


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
def test_zarinpal_payment_request__failed(
    zarinpal_provider: ZarinpalProvider,
    responses: RequestsMock,
    order_details: OrderDetails,
    errors: JSONDocument,
) -> None:
    responses.add(
        responses.POST,
        "https://az.bank/request/",
        json={"data": {}, "errors": errors},
        status=422,
    )

    with pytest.raises(InternalRejectPaymentError):
        assert zarinpal_provider.create_payment_request(order_details)


@pytest.mark.parametrize("side_effect", [ConnectionError, Timeout])
def test_zarinpal_payment_request__failed_with_side_effect(
    zarinpal_provider: ZarinpalProvider,
    responses: RequestsMock,
    side_effect: type[Exception],
    order_details: OrderDetails,
) -> None:
    responses.add(
        responses.POST,
        "https://az.bank/request/",
        body=side_effect(),
    )

    with pytest.raises(InternalConnectionError):
        assert zarinpal_provider.create_payment_request(order_details)


def test_zarinpal_payment_reqeust__minimum_amount(
    zarinpal_provider: ZarinpalProvider,
    order_details: OrderDetails,
) -> None:
    order_details.amount = Decimal(100)

    with pytest.raises(InternalMinimumAmountError):
        assert zarinpal_provider.create_payment_request(order_details)


@pytest.mark.parametrize(
    "verify_code,is_verified,description",
    [
        (
            100,
            True,
            "Verified",
        ),
        (
            101,
            True,
            "Already Verified",
        ),
        (
            -8,
            False,
            "Cancelled",
        ),
    ],
)
def test_zarinpal_verify(
    responses: RequestsMock,
    zarinpal_provider: ZarinpalProvider,
    verify_code: int,
    is_verified: bool,
    description: str,
) -> None:
    verify_response = {
        "data": {
            "code": verify_code,
            "message": description,
            "card_hash": "1EBE3EBEBE35C",
            "card_pan": "502229******5995",
            "ref_id": 201,
            "fee_type": "Merchant",
            "fee": 0,
        },
        "errors": [],
    }
    responses.add(
        responses.POST,
        "https://az.bank/verify/",
        json=verify_response,
        status=200,
    )

    assert zarinpal_provider.verify_payment("123", Decimal("100")) == is_verified


def test_zarinpal_verify__invalid_gateway_response(
    responses: RequestsMock, zarinpal_provider: ZarinpalProvider
) -> None:
    verify_response = {
        "data": {
            "card_hash": "1EBE3EBEBE35C",
            "card_pan": "502229******5995",
            "ref_id": 201,
            "fee_type": "Merchant",
            "fee": 0,
        },
        "errors": [],
    }
    responses.add(
        responses.POST,
        "https://az.bank/verify/",
        json=verify_response,
        status=200,
    )

    with pytest.raises(InternalInvalidGatewayResponseError):
        zarinpal_provider.verify_payment("123", Decimal("100"))


def test_zarinpal_reverse_payment__successful(
    responses: RequestsMock, zarinpal_provider: ZarinpalProvider
) -> None:
    reverse_response = {"data": {"code": 100, "message": "Reversed"}, "errors": []}
    responses.add(
        responses.POST,
        "https://az.bank/reverse/",
        json=reverse_response,
        status=200,
    )

    assert zarinpal_provider.reverse_payment("123") is True


def test_zarinpal_reverse_payment__failed(
    responses: RequestsMock, zarinpal_provider: ZarinpalProvider
) -> None:
    reverse_response = {
        "data": {},
        "errors": {"message": "Terminal ip limit most be active.", "code": -62, "validations": []},
    }
    responses.add(
        responses.POST,
        "https://az.bank/reverse/",
        json=reverse_response,
        status=200,
    )

    with pytest.raises(InternalRejectPaymentError):
        zarinpal_provider.reverse_payment("123")


def test_zarinpal_reverse_payment__invalid_gateway_response(
    responses: RequestsMock, zarinpal_provider: ZarinpalProvider
) -> None:
    reverse_response = {"data": {"message": "Reversed"}, "errors": []}
    responses.add(
        responses.POST,
        "https://az.bank/reverse/",
        json=reverse_response,
        status=200,
    )

    with pytest.raises(InternalInvalidGatewayResponseError):
        zarinpal_provider.reverse_payment("123")


def test_zarinpal_inquiry_payment(responses: RequestsMock, zarinpal_provider: ZarinpalProvider) -> None:
    response = {"data": {"status": "PAID", "code": 100, "message": "Success"}, "errors": []}
    responses.add(
        responses.POST,
        "https://az.bank/inquiry/",
        json=response,
        status=200,
    )

    assert zarinpal_provider.inquiry_payment("123") == PaymentStatus.PAID


def test_zarinpal_inquiry_payment__invalid_response(
    responses: RequestsMock, zarinpal_provider: ZarinpalProvider
) -> None:
    response = {"data": {"code": 100, "message": "Success"}, "errors": []}
    responses.add(
        responses.POST,
        "https://az.bank/inquiry/",
        json=response,
        status=200,
    )

    with pytest.raises(InternalInvalidGatewayResponseError):
        zarinpal_provider.inquiry_payment("123")
