from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from azbankgateways.v3.exceptions.internal import (
    InternalInvalidGatewayConfigError,
    InternalInvalidGatewayResponseError,
    InternalRejectPaymentError,
)
from azbankgateways.v3.http import URL, HttpHeaders
from azbankgateways.v3.interfaces import (
    CallbackURLType,
    HttpClientInterface,
    HttpHeadersInterface,
    HttpMethod,
    HttpRequestInterface,
    HttpResponseInterface,
    MessageServiceInterface,
    MessageType,
    OrderDetails,
    PaymentGatewayConfigInterface,
    PaymentInquiryResult,
    PaymentStatus,
    ProviderInterface,
)
from azbankgateways.v3.mixins.check_dataclass_fields import CheckDataclassFieldsMixin
from azbankgateways.v3.mixins.minimum_amount_check import MinimumAmountCheckMixin


# TODO: Ensure all subclasses of PaymentGatewayConfigInterface are
#  decorated with @dataclass(frozen=True, slots=True).
@dataclass(frozen=True, slots=True)
class ZarinpalPaymentGatewayConfig(CheckDataclassFieldsMixin, PaymentGatewayConfigInterface):
    merchant_code: str
    callback_url_generator: CallbackURLType

    payment_request_url: URL = field(default=URL("https://payment.zarinpal.com/pg/v4/payment/request.json/"))
    start_payment_url: URL = field(default=URL("https://payment.zarinpal.com/pg/StartPay/"))
    verify_payment_url: URL = field(default=URL("https://payment.zarinpal.com/pg/v4/payment/verify.json"))
    reverse_payment_url: URL = field(default=URL("https://payment.zarinpal.com/pg/v4/payment/reverse.json"))
    inquiry_payment_url: URL = field(default=URL("https://payment.zarinpal.com/pg/v4/payment/inquiry.json"))
    http_requests_timeout: int = 20

    def __post_init__(self) -> None:
        self.check_fields(error_class=InternalInvalidGatewayConfigError)


class ZarinpalProvider(MinimumAmountCheckMixin, ProviderInterface):
    _PAYMENT_VERIFIED_STATUS_CODES = {100, 101}
    _REVERSED_SUCCESS_CODE = 100
    _PAYMENT_STATUSES = {
        'IN_BANK': PaymentStatus.PENDING,
        'PAID': PaymentStatus.PAID,
        'VERIFIED': PaymentStatus.VERIFIED,
        'FAILED': PaymentStatus.FAILED,
        'REVERSED': PaymentStatus.RESERVED,
    }

    def __init__(
        self,
        config: ZarinpalPaymentGatewayConfig,
        message_service: MessageServiceInterface,
        http_client: HttpClientInterface,
        http_request_class: type[HttpRequestInterface],
        http_headers_class: type[HttpHeadersInterface],
    ) -> None:
        self._config = config
        self._message_service = message_service
        self._http_client = http_client
        self._http_request_class = http_request_class
        self._http_headers_class = http_headers_class

    @property
    def minimum_amount(self) -> Decimal:
        return Decimal(1000)

    def create_payment_request(self, order_details: OrderDetails) -> HttpRequestInterface:
        # TODO: move check_minimum_amount function to PaymentGateway once `PaymentGateway` is implemented.
        self.check_minimum_amount(order_details)
        data = {
            'merchant_id': self._config.merchant_code,
            'amount': int(order_details.amount),
            'callback_url': self._config.callback_url_generator(order_details),
            'description': self._message_service.generate_message(
                MessageType.DESCRIPTION,
                {
                    "tracking_code": order_details.tracking_code,
                },
            ),
            'metadata': {
                k: v
                for k, v in {
                    "mobile": order_details.phone_number,
                    "email": order_details.email,
                    "order_id": order_details.order_id,
                }.items()
                if v
            },
            "currency": "IRR",
        }
        http_response = self._send_request(self._config.payment_request_url, data=data)
        payment_token = http_response.get("data", {}).get("authority")
        if not payment_token:
            raise InternalInvalidGatewayResponseError(
                "Payment request failed: `authority` token missing in gateway response."
            )
        redirect_url = self._config.start_payment_url.join(payment_token)
        return self._http_request_class(
            http_method=HttpMethod.GET, url=redirect_url, timeout=self._config.http_requests_timeout
        )

    def verify_payment(self, reference_number: str, amount: Decimal) -> bool:
        data = {
            'merchant_id': self._config.merchant_code,
            'authority': reference_number,
            'amount': int(amount),
        }
        http_response = self._send_request(self._config.verify_payment_url, data=data)
        status_code = http_response.get("data", {}).get("code")
        if not status_code:
            raise InternalInvalidGatewayResponseError(
                "Payment verification failed: `code` field missing in gateway response."
            )
        return status_code in self._PAYMENT_VERIFIED_STATUS_CODES

    def reverse_payment(self, reference_number: str) -> bool:
        data = {
            "merchant_id": self._config.merchant_code,
            "authority": reference_number,
        }
        http_response = self._send_request(self._config.reverse_payment_url, data=data)
        status_code = http_response.get('data', {}).get('code')
        if not status_code:
            raise InternalInvalidGatewayResponseError(
                "Reverse payment failed: `code` field missing in gateway response."
            )
        if status_code == self._REVERSED_SUCCESS_CODE:
            return True
        return False

    def inquiry_payment(self, reference_number: str) -> PaymentInquiryResult:
        data = {
            "merchant_id": self._config.merchant_code,
            "authority": reference_number,
        }
        response = self._send_request(self._config.inquiry_payment_url, data=data)
        status = response.get("data", {}).get("status")
        if not status:
            raise InternalInvalidGatewayResponseError(
                "inquiry payment failed: `status` field missing in gateway response."
            )
        return PaymentInquiryResult(status=self._PAYMENT_STATUSES[status], extra_information=response['data'])

    @classmethod
    def _check_response(cls, response: HttpResponseInterface) -> None:
        errors = response.json().get('errors')

        if errors:
            if isinstance(errors, dict):
                # Single error dict
                message = errors.get("message", str(errors))
            elif isinstance(errors, list):
                # Multiple errors
                message = "; ".join(err.get("message", str(err)) for err in errors)
            else:
                # Unexpected type
                message = str(errors)

            raise InternalRejectPaymentError(message)

        if not response.ok:
            raise InternalRejectPaymentError(response.body)

    def _send_request(
        self, url: URL, data: dict[str, Any], method: HttpMethod = HttpMethod.POST
    ) -> dict[str, Any]:
        headers = HttpHeaders(
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
        )
        http_request = self._http_request_class(
            method, url, data=data, timeout=self._config.http_requests_timeout, headers=headers
        )
        http_response = self._http_client.send(http_request)
        self._check_response(http_response)
        return http_response.json()
