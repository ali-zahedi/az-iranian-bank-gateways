from dataclasses import MISSING, dataclass, field
from decimal import Decimal
from typing import Self

from azbankgateways.v3.exceptions.internal import InternalRejectPaymentError
from azbankgateways.v3.http_utils import URL
from azbankgateways.v3.interfaces import (
    CallbackURLType,
    HttpClientInterface,
    HttpMethod,
    HttpRequestInterface,
    HttpResponseInterface,
    MessageServiceInterface,
    MessageType,
    OrderDetails,
    PaymentGatewayConfigInterface,
    ProviderInterface,
)
from azbankgateways.v3.mixins import MinimumAmountCheckMixin, NoDirectInitMixin


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


class ZarinpalProvider(MinimumAmountCheckMixin, NoDirectInitMixin, ProviderInterface):
    def __init__(
        self,
        config: ZarinpalPaymentGatewayConfig,
        message_service: MessageServiceInterface,
        http_client: HttpClientInterface,
        http_request_cls: type[HttpRequestInterface],
    ) -> None:
        super().__init__(config, message_service, http_client, http_request_cls)

        assert config, "Config is required"
        assert message_service, "Message service is required"

        self.__config = config
        self.__message_service = message_service
        self.__http_client = http_client
        self.__http_request_cls = http_request_cls

    @classmethod
    def create(
        cls,
        config: ZarinpalPaymentGatewayConfig,
        message_service: MessageServiceInterface,
        http_client: HttpClientInterface,
        http_request_cls: type[HttpRequestInterface],
    ) -> Self:
        return super().create(config, message_service, http_client, http_request_cls)

    @property
    def minimum_amount(self) -> Decimal:
        return Decimal(1000)

    def create_payment_request(self, order_details: OrderDetails) -> HttpRequestInterface:
        payment_token = self._create_payment_token(order_details)
        url = URL(self.__config.start_payment_url.join(payment_token))
        return self.__http_request_cls.create(
            http_method=HttpMethod.GET, url=url, timeout=self.__config.http_requests_timeout
        )

    def _create_payment_token(self, order_details: OrderDetails) -> str:
        self.check_minimum_amount(order_details)
        http_request = self._build_payment_token_http_request(order_details)
        http_response = self.__http_client.send(http_request)
        self._check_response(http_response)
        return http_response.json()["data"]["authority"]

    def _build_payment_token_http_request(self, order_details: OrderDetails) -> HttpRequestInterface:
        description = self.__message_service.generate_message(
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
            'merchant_id': self.__config.merchant_code,
            'amount': int(order_details.amount),
            'callback_url': self.__config.callback_url_generator(order_details),
            'description': description,
            'metadata': {k: v for k, v in metadata.items() if v},
            "currency": "IRR",
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        return self.__http_request_cls.create(
            HttpMethod.POST,
            self.__config.payment_request_url,
            headers=headers,
            data=data,
            timeout=self.__config.http_requests_timeout,
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
