from dataclasses import MISSING, dataclass, field
from decimal import Decimal

from azbankgateways.v3.exceptions.internal import InternalRejectPaymentError
from azbankgateways.v3.http import URL, HttpRequest
from azbankgateways.v3.interfaces import (
    CallbackURLType,
    HttpMethod,
    HttpResponseInterface,
    MessageType,
    OrderDetails,
    PaymentGatewayConfigInterface,
)
from azbankgateways.v3.providers.provider import Provider


# TODO: Ensure all subclasses of PaymentGatewayConfigInterface are
#  decorated with @dataclass(frozen=True, slots=True).
@dataclass(frozen=True, slots=True)
class ZarinpalPaymentGatewayConfig(PaymentGatewayConfigInterface):
    merchant_code: str = field(default=MISSING)

    # TODO: Using `MISSING` as the default currently causes the IDE to show
    #       "Literal[_MISSING_TYPE.MISSING] object is not callable".
    #       Investigate and fix this issue.
    callback_url_generator: CallbackURLType = field(default=MISSING)

    payment_request_url: URL = field(default=URL("https://payment.zarinpal.com/pg/v4/payment/request.json/"))
    start_payment_url: URL = field(default=URL("https://payment.zarinpal.com/pg/StartPay/"))
    http_requests_timeout: int = 20

    def __post_init__(self) -> None:
        if not self.merchant_code:
            raise ValueError("Merchant code is required")
        if not self.callback_url_generator:
            raise ValueError("Callback url generator is required")
        if not isinstance(self.payment_request_url, URL):
            raise TypeError("payment_request_url must be a URL instance")
        if not isinstance(self.start_payment_url, URL):
            raise TypeError("start_payment_url must be a URL instance")


class ZarinpalProvider(Provider):
    @property
    def minimum_amount(self) -> Decimal:
        return Decimal(1000)

    def create_payment_request(self, order_details: OrderDetails) -> HttpRequest:
        payment_token = self._create_payment_token(order_details)
        url = URL(self.config.start_payment_url.join(payment_token))
        return self.http_request_cls(
            http_method=HttpMethod.GET, url=url, timeout=self.config.http_requests_timeout
        )

    def _create_payment_token(self, order_details: OrderDetails) -> str:
        self.check_minimum_amount(order_details)
        http_request = self._build_payment_token_http_request(order_details)
        http_response = self.http_client.send(http_request)
        self._check_response(http_response)
        return http_response.json()["data"]["authority"]

    def _build_payment_token_http_request(self, order_details: OrderDetails) -> HttpRequest:
        description = self.message_service.generate_message(
            MessageType.DESCRIPTION,
            {
                "tracking_code": order_details.tracking_code,
            },
        )
        metadata = {
            "mobile": order_details.phone_number,
            "email": order_details.email,
            "order_id": order_details.order_id,
        }
        data = {
            'merchant_id': self.config.merchant_code,
            'amount': int(order_details.amount),
            'callback_url': self.config.callback_url_generator(order_details),
            'description': description,
            'metadata': {k: v for k, v in metadata.items() if v},
            "currency": "IRR",
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        return self.http_request_cls(
            HttpMethod.POST,
            self.config.payment_request_url,
            headers=headers,
            data=data,
            timeout=self.config.http_requests_timeout,
        )

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
