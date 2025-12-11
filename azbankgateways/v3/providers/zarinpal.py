import decimal
from dataclasses import MISSING, dataclass, field
from decimal import Decimal

from azbankgateways.v3.exceptions.internal import (
    InternalInvalidGatewayResponseError,
    InternalMinimumAmountError,
    InternalRejectPaymentError,
)
from azbankgateways.v3.http import URL
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
    ProviderInterface,
)
from azbankgateways.v3.mixins.minimum_amount_check import MinimumAmountCheckMixin


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
    verify_payment_url: URL = field(default=URL("https://payment.zarinpal.com/pg/v4/payment/verify.json"))
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


class ZarinpalProvider(MinimumAmountCheckMixin, ProviderInterface):
    PAYMENT_VERIFIED_STATUS_CODES = [100, 101]

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
        payment_token = self._create_payment_token(order_details)
        url = self._config.start_payment_url.join(payment_token)
        return self._http_request_class(
            http_method=HttpMethod.GET, url=url, timeout=self._config.http_requests_timeout
        )

    def verify_payment(self, reference_number: str, amount: Decimal) -> bool:
        http_request = self._build_verify_payment_http_request(reference_number, amount)
        http_response = self._http_client.send(http_request)
        self._check_response(http_response)
        json_body = http_response.json()
        data = json_body.get("data")
        if not data or "code" not in data or "message" not in data:
            raise InternalInvalidGatewayResponseError(
                "Invalid verify payment response: missing required fields"
            )
        return data['code'] in self.PAYMENT_VERIFIED_STATUS_CODES

    def _create_payment_token(self, order_details: OrderDetails) -> str:
        # TODO: move check_minimum_amount function to PaymentGateway once `PaymentGateway` is implemented.
        self.check_minimum_amount(order_details)

        http_request = self._build_payment_token_http_request(order_details)
        http_response = self._http_client.send(http_request)
        self._check_response(http_response)
        return http_response.json()["data"]["authority"]

    def _build_payment_token_http_request(self, order_details: OrderDetails) -> HttpRequestInterface:
        description = self._message_service.generate_message(
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
            'merchant_id': self._config.merchant_code,
            'amount': int(order_details.amount),
            'callback_url': self._config.callback_url_generator(order_details),
            'description': description,
            'metadata': {k: v for k, v in metadata.items() if v},
            "currency": "IRR",
        }
        headers = self._http_headers_class(
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
        )
        return self._http_request_class(
            HttpMethod.POST,
            self._config.payment_request_url,
            headers=headers,
            data=data,
            timeout=self._config.http_requests_timeout,
        )

    def _build_verify_payment_http_request(
        self, reference_number: str, amount: decimal.Decimal
    ) -> HttpRequestInterface:
        data = {
            'merchant_id': self._config.merchant_code,
            'authority': reference_number,
            'amount': int(amount),
        }
        headers = self._http_headers_class(
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
        )
        return self._http_request_class(
            HttpMethod.POST,
            self._config.verify_payment_url,
            headers=headers,
            data=data,
            timeout=self._config.http_requests_timeout,
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

    def check_minimum_amount(self, order_details: OrderDetails) -> None:
        if order_details.amount < self.minimum_amount:
            raise InternalMinimumAmountError(order_details, self.minimum_amount)
