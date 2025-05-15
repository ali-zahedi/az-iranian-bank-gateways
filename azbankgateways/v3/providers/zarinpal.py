from __future__ import annotations

import logging
from decimal import Decimal
from typing import TYPE_CHECKING
from typing import cast

import requests

from azbankgateways.exceptions.exceptions import BankGatewayConnectionError
from azbankgateways.exceptions.exceptions import BankGatewayRejectPayment
from azbankgateways.v3.currencies import CurrencyRegistry
from azbankgateways.v3.interfaces import HttpMethod
from azbankgateways.v3.interfaces import MessageType
from azbankgateways.v3.interfaces import PaymentGatewayConfigInterface
from azbankgateways.v3.interfaces import ProviderInterface
from azbankgateways.v3.redirect_request import RedirectRequest

if TYPE_CHECKING:
    from typing import Any

    from azbankgateways.v3.interfaces import CallbackURLType
    from azbankgateways.v3.interfaces import Currency
    from azbankgateways.v3.interfaces import MessageServiceInterface
    from azbankgateways.v3.interfaces import OrderDetails
    from azbankgateways.v3.interfaces import RequestInterface


class ZarinpalPaymentGatewayConfig(PaymentGatewayConfigInterface):
    def __init__(
        self,
        merchant_code: str,
        callback_url: CallbackURLType,
        payment_request_url: str | None = None,
        start_payment_url: str | None = None,
        currency: Currency | None = None,
    ):
        assert merchant_code, "Merchant code is required"
        assert callback_url, "Callback url is required"  # type: ignore[truthy-function]

        if not currency:
            currency = CurrencyRegistry.get_currency("IRT")

        if not payment_request_url:
            payment_request_url = "https://payment.zarinpal.com/pg/v4/payment/request.json"

        if not start_payment_url:
            start_payment_url = "https://payment.zarinpal.com/pg/StartPay/"

        self.__merchant_code = merchant_code
        self.__callback_url = callback_url
        self.__currency = currency
        self.__payment_request_url = payment_request_url
        self.__start_payment_url = start_payment_url.strip("/")

    @property
    def merchant_code(self) -> str:
        return self.__merchant_code

    @property
    def payment_request_url(self) -> str:
        return self.__payment_request_url

    @property
    def start_payment_url(self) -> str:
        return self.__start_payment_url

    @property
    def currency(self) -> Currency:
        return self.__currency

    @property
    def callback_url(self) -> CallbackURLType:
        return self.__callback_url


class ZarinpalProvider(ProviderInterface):
    def __init__(
        self,
        config: ZarinpalPaymentGatewayConfig,
        message_service: MessageServiceInterface,
        order_details: OrderDetails,
    ):
        assert config, "Config is required"
        assert message_service, "Message service is required"

        self.__config = config
        self.__message_service = message_service
        self.__order_details = order_details

    @property
    def currency(self) -> Currency:
        return self.__config.currency

    @property
    def minimum_amount(self) -> Decimal:
        return Decimal(1000)

    def get_request_pay(self) -> RequestInterface:
        return RedirectRequest(
            http_method=HttpMethod.GET,
            url=f"{self.__config.start_payment_url}/{self.__pay()}",
        )

    def get_payment_redirect_method(self) -> HttpMethod:
        raise NotImplementedError()

    def get_payment_request_body(self) -> dict[str, Any] | None:
        raise NotImplementedError()

    def get_payment_gateway_url(self) -> str:
        raise NotImplementedError()

    def __get_final_amount(self) -> Decimal:
        # TODO: get rid of this method, TEMP method, converting IRT to IRR or vice versa,
        #  should support multiple currencies. Consider using a service or interface to handle the conversion process,
        #  where the input includes the amount, source currency, and target currency.
        return self.__order_details.amount

    def __get_pay_data(self) -> dict[str, Any]:
        description = self.__message_service.generate_message(
            MessageType.DESCRIPTION,
            {
                "tracking_code": self.__order_details.tracking_code,
            },
        )

        metadata = {}
        if self.__order_details.phone_number:
            metadata["mobile"] = self.__order_details.phone_number
        if self.__order_details.email:
            metadata["email"] = self.__order_details.email
        if self.__order_details.order_id:
            metadata["order_id"] = self.__order_details.order_id

        return {
            "merchant_id": self.__config.merchant_code,
            "amount": str(self.__get_final_amount()),
            "callback_url": self.__config.callback_url(self.__order_details),
            "description": description,
            "currency": self.currency.value,
            "metadata": metadata,
        }

    def __pay(self) -> str:
        if self.__order_details.amount < self.minimum_amount:
            raise BankGatewayRejectPayment(
                self.__message_service.generate_message(
                    MessageType.MINIMUM_AMOUNT,
                    context={"minimum_amount": self.minimum_amount},
                )
            )

        data = self.__get_pay_data()
        result = self._send_data(self.__config.payment_request_url, data).get("data", {})

        if not result:
            logging.critical("Zarinpal gateway reject payment")
            raise BankGatewayRejectPayment

        if str(result.get("code", "")) == "100" and not result.get("errors", []):
            token = result.get("authority")
            logging.critical("Token is %s", token)
            return cast(str, token)
        else:
            logging.critical("Zarinpal gateway reject payment")
            raise BankGatewayRejectPayment

    def _send_data(self, api: str, json: Any | None) -> Any:
        try:
            response = requests.post(api, json=json, timeout=5)
        except requests.Timeout:
            logging.exception(f"Zarinpal time out gateway {json}")
            raise BankGatewayConnectionError() from None
        except requests.ConnectionError:
            logging.exception(f"Zarinpal time out gateway {json}")
            raise BankGatewayConnectionError() from None

        try:
            response.raise_for_status()
        except requests.HTTPError:
            logging.exception(f"Zarinpal error {json}")  # WTF
            raise BankGatewayRejectPayment(self.__extract_error(response.json())) from None

        return response.json()

    @classmethod
    def __extract_error(cls, data: dict[str, Any]) -> list[str]:
        assert isinstance(data, dict), "Data must be dict"

        errors_message = []
        errors_response = data.get("errors", [])
        if isinstance(errors_response, list):
            errors_message = [error.get("message") for error in errors_response if error.get("message")]
        elif isinstance(errors_response, dict):
            errors_message = [errors_response.get("message", "")]
        return errors_message
