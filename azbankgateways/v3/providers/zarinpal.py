import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

import requests

from azbankgateways.exceptions.exceptions import (
    BankGatewayConnectionError,
    BankGatewayRejectPayment,
)
from azbankgateways.v3.currencies import CurrencyRegistry
from azbankgateways.v3.interfaces import (
    CallbackURLType,
    Currency,
    HttpMethod,
    MessageServiceInterface,
    MessageType,
    OrderDetails,
    PaymentGatewayConfigInterface,
    ProviderInterface,
    RedirectRequestInterface,
)
from azbankgateways.v3.redirect_request import RedirectRequest


class ZarinpalPaymentGatewayConfig(PaymentGatewayConfigInterface):
    def __init__(
        self,
        merchant_code: str,
        callback_url: CallbackURLType,
        payment_request_url: Optional[str] = None,
        start_payment_url: Optional[str] = None,
        currency: Optional[Currency] = None,
    ):
        assert merchant_code, "Merchant code is required"
        assert callback_url, "Callback url is required"

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
        self.__start_payment_url = start_payment_url.strip('/')

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

    def get_request_pay(self) -> RedirectRequestInterface:
        return RedirectRequest(
            http_method=HttpMethod.GET,
            url=f'{self.__config.start_payment_url}/{self.__pay()}',
        )

    def get_payment_redirect_method(self) -> HttpMethod:
        raise NotImplementedError()

    def get_payment_request_body(self) -> Optional[Dict[str, Any]]:
        raise NotImplementedError()

    def get_payment_gateway_url(self) -> str:
        raise NotImplementedError()

    def __get_final_amount(self) -> Decimal:
        # TODO: get rid of this method, TEMP method, converting IRT to IRR or vice versa,
        #  should support multiple currencies. Consider using a service or interface to handle the conversion process,
        #  where the input includes the amount, source currency, and target currency.
        return self.__order_details.amount

    def __get_pay_data(self) -> Dict[str, Any]:
        description = self.__message_service.generate_message(
            MessageType.DESCRIPTION,
            {
                "tracking_code": self.__order_details.tracking_code,
            },
        )

        metadata = {}
        if self.__order_details.phone_number:
            metadata['mobile'] = self.__order_details.phone_number
        if self.__order_details.email:
            metadata['email'] = self.__order_details.email
        if self.__order_details.order_id:
            metadata['order_id'] = self.__order_details.order_id

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
                    MessageType.MINIMUM_AMOUNT, context={'minimum_amount': self.minimum_amount}
                )
            )

        data = self.__get_pay_data()
        result = self._send_data(self.__config.payment_request_url, data).get('data', {})

        if not result:
            logging.critical("Zarinpal gateway reject payment")
            raise BankGatewayRejectPayment

        if str(result.get("code", "")) == "100" and not result.get("errors", []):
            token = result.get('authority')
            logging.critical("Toke is %s" % (token))
            return token
        else:
            logging.critical("Zarinpal gateway reject payment")
            raise BankGatewayRejectPayment

    def _send_data(self, api, data):
        try:
            response = requests.post(api, json=data, timeout=5)
        except requests.Timeout:
            logging.exception("Zarinpal time out gateway {}".format(data))
            raise BankGatewayConnectionError()
        except requests.ConnectionError:
            logging.exception("Zarinpal time out gateway {}".format(data))
            raise BankGatewayConnectionError()

        try:
            response.raise_for_status()
        except requests.HTTPError:
            logging.exception("Zarinpal error {}".format(data))  # WTF
            raise BankGatewayRejectPayment(self.__extract_error(response.json()))

        return response.json()

    @classmethod
    def __extract_error(cls, data: Dict[str, Any]) -> List[str]:
        assert isinstance(data, dict), "Data must be dict"

        errors_message = []
        errors_response = data.get('errors', [])
        if isinstance(errors_response, list):
            errors_message = [error.get('message') for error in errors_response if error.get('message')]
        elif isinstance(errors_response, dict):
            errors_message = [errors_response.get('message', '')]
        return errors_message
