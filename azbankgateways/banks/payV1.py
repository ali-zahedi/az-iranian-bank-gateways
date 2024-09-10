import json
import logging

import requests
from requests import HTTPError, JSONDecodeError, Timeout

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import BankGatewayConnectionError, SettingDoesNotExist
from azbankgateways.exceptions.exceptions import (
    BankGatewayRejectPayment,
    BankGatewayStateInvalid,
)
from azbankgateways.models import BankType, CurrencyEnum, PaymentStatus


class PayV1(BaseBank):
    _merchant_code = None
    _x_sandbox = None

    def __init__(self, **kwargs):
        super(PayV1, self).__init__(**kwargs)
        self.set_gateway_currency(CurrencyEnum.IRR)
        self._token_api_url = "https://pay.ir/pg/send"
        self._payment_url = "https://pay.ir/pg/{}"
        self._verify_api_url = "https://pay.ir/pg/verify"

    def get_bank_type(self):
        return BankType.PAYV1

    def set_default_settings(self):
        for item in ["MERCHANT_CODE", "X_SANDBOX"]:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist()
            setattr(self, f"_{item.lower()}", self.default_setting_kwargs[item])

        self._merchant_code = self._merchant_code if not self._x_sandbox else "test"

    """
    gateway
    """

    def _get_gateway_payment_url_parameter(self):
        return self._payment_url.format(self._reference_number)

    def _get_gateway_payment_parameter(self):
        return {}

    def _get_gateway_payment_method_parameter(self):
        return "GET"

    """
    pay
    """

    def get_pay_data(self):
        data = {
            "api": self._merchant_code,
            "amount": self.get_gateway_amount(),
            "redirect": self._get_gateway_callback_url(),
            "mobile": self.get_mobile_number(),
            "factorNumber": self.get_tracking_code(),
        }
        return data

    def prepare_pay(self):
        super(PayV1, self).prepare_pay()

    def pay(self):
        super(PayV1, self).pay()
        data = self.get_pay_data()
        response = self._send_data(self._token_api_url, data)
        response_json = response.json()
        if response.status_code == 200 and int(response_json["status"]) == 1:
            token = response_json["token"]
            self._set_reference_number(token)
        else:
            logging.critical(
                "PayV1 gateway reject payment with error code {0} and status code {1}".format(
                    response_json["errorCode"], response.status_code
                )
            )
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    """
    verify gateway
    """

    def prepare_verify_from_gateway(self):
        super(PayV1, self).prepare_verify_from_gateway()
        request = self.get_request()
        for method in [
            "GET",
            "POST",
        ]:
            token = getattr(request, method, {}).get("token")

            if token:
                self._set_reference_number(token)
                self._set_bank_record()
                break
        else:
            raise BankGatewayStateInvalid

    def verify_from_gateway(self, request):
        super(PayV1, self).verify_from_gateway(request)

    """
    verify
    """

    def get_verify_data(self):
        super(PayV1, self).get_verify_data()
        data = {"api": self._merchant_code, "token": self.get_reference_number(), "status": self._bank.status}
        return data

    def prepare_verify(self, tracking_code):
        super(PayV1, self).prepare_verify(tracking_code)

    def verify(self, tracking_code):
        super(PayV1, self).verify(tracking_code)
        data = self.get_verify_data()
        try:
            response = self._send_data(self._verify_api_url, data, timeout=10)
            response.raise_for_status()
            response_json = response.json()
            status = str(response_json.get("status", 0))
            if status == '1':
                status = PaymentStatus.COMPLETE
                extra_information = json.dumps(response_json)
                self._bank.extra_information = extra_information
            else:
                status = PaymentStatus.ERROR
        except (JSONDecodeError, HTTPError, Timeout):
            status = PaymentStatus.ERROR

        self._set_payment_status(status)
        self._bank.save()

    def _send_data(self, url, data, timeout=5) -> requests.post:
        try:
            logging.debug("Sending POST request to {} with data {}".format(url, data))
            response = requests.post(url, json=data, timeout=timeout)
        except requests.Timeout:
            logging.exception("PayV1 time out gateway {}".format(data))
            raise BankGatewayConnectionError()
        except requests.ConnectionError:
            logging.exception("PayV1 time out gateway {}".format(data))
            raise BankGatewayConnectionError()

        return response
