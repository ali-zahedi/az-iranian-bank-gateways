import logging
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, List, Optional

import requests

from azbankgateways.exceptions.exceptions import (
    BankGatewayConnectionError,
    BankGatewayRejectPayment,
)
from azbankgateways.v3.interfaces import (
    CallbackURLType,
    HttpMethod,
    MessageServiceInterface,
    MessageType,
    OrderDetails,
    PaymentGatewayConfigInterface,
    ProviderInterface,
    RequestInterface,
)
from azbankgateways.v3.redirect_request import RedirectRequest


# TODO: Ensure all subclasses of PaymentGatewayConfigInterface are
#  decorated with @dataclass(frozen=True, slots=True).
@dataclass(frozen=True, slots=True)
class ZarinpalPaymentGatewayConfig(PaymentGatewayConfigInterface):
    merchant_code: str
    callback_url_generator: CallbackURLType
    payment_request_url: str = field(default="https://payment.zarinpal.com/pg/v4/payment/request.json/")
    start_payment_url: str = field(default="https://payment.zarinpal.com/pg/StartPay/")

    def __post_init__(self):
        if not self.merchant_code:
            raise ValueError("Merchant code is required")
        if not self.callback_url_generator:
            raise ValueError("Callback url generator is required")


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
    def minimum_amount(self) -> Decimal:
        return Decimal(1000)

    def get_request_pay(self) -> RequestInterface:
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
            "callback_url": self.__config.callback_url_generator(self.__order_details),
            "description": description,
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
