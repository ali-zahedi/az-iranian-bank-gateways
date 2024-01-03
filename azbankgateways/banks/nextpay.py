import json
import logging

import requests

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import BankGatewayConnectionError, SettingDoesNotExist
from azbankgateways.exceptions.exceptions import BankGatewayRejectPayment
from azbankgateways.models import BankType, CurrencyEnum, PaymentStatus
from azbankgateways.utils import get_json, split_to_dict_querystring


class Nextpay(BaseBank):
    _merchant_code = None
    _params = {}

    def __init__(self, **kwargs):
        super(Nextpay, self).__init__(**kwargs)
        self.set_gateway_currency(CurrencyEnum.IRR)
        self._token_api_url = "https://nextpay.org/nx/gateway/token"
        self._verify_api_url = "https://nextpay.org/nx/gateway/verify"

    def get_bank_type(self):
        return BankType.NEXTPAY

    def set_default_settings(self):
        for item in ["MERCHANT_CODE"]:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist()
            setattr(self, f"_{item.lower()}", self.default_setting_kwargs[item])

    """
    gateway
    """

    def _get_gateway_payment_url_parameter(self):
        return self._payment_url

    def _get_gateway_payment_parameter(self):
        params = {}
        params.update(self._params)
        return params

    def _get_gateway_payment_method_parameter(self):
        return "GET"

    """
    pay
    """

    def get_pay_data(self):
        data = {
            "order_id": self.get_tracking_code(),
            "amount": self.get_gateway_amount(),
            "phone": self.get_mobile_number(),
            "callback": self._get_gateway_callback_url(),
        }
        return data

    def prepare_pay(self):
        super(Nextpay, self).prepare_pay()

    def pay(self):
        super(Nextpay, self).pay()
        data = self.get_pay_data()
        response_json = self._send_data(self._token_api_url, data)
        if "id" in response_json and "link" in response_json and response_json["link"] and response_json["id"]:
            token = response_json["id"]
            self._params = split_to_dict_querystring(response_json["link"])
            self._set_reference_number(token)
        else:
            logging.critical("Nextpay gateway reject payment")
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    """
    verify gateway
    """

    def prepare_verify_from_gateway(self):
        super(Nextpay, self).prepare_verify_from_gateway()
        for method in ["GET", "POST", "data"]:
            token = getattr(self.get_request(), method).get("id", None)
            if token:
                self._set_reference_number(token)
                self._set_bank_record()
                break

    def verify_from_gateway(self, request):
        super(Nextpay, self).verify_from_gateway(request)

    """
    verify
    """

    def get_verify_data(self):
        super(Nextpay, self).get_verify_data()
        data = {
            "id": self.get_reference_number(),
            "order_id": self.get_tracking_code(),
        }
        return data

    def prepare_verify(self, tracking_code):
        super(Nextpay, self).prepare_verify(tracking_code)

    def verify(self, transaction_code):
        super(Nextpay, self).verify(transaction_code)
        data = self.get_verify_data()
        response_json = self._send_data(self._verify_api_url, data, timeout=10)
        if response_json.get("verify", {}).get("date", None):
            self._set_payment_status(PaymentStatus.COMPLETE)
            extra_information = json.dumps(response_json)
            self._bank.extra_information = extra_information
            self._bank.save()
        else:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
            logging.debug("Nextpay gateway unapproved payment")

    def _send_data(self, api, data, timeout=5):
        headers = {
            "X-API-KEY": self._merchant_code,
        }
        try:
            response = requests.post(api, headers=headers, json=data, timeout=timeout)
        except requests.Timeout:
            logging.exception("Nextpay time out gateway {}".format(data))
            raise BankGatewayConnectionError()
        except requests.ConnectionError:
            logging.exception("Nextpay time out gateway {}".format(data))
            raise BankGatewayConnectionError()

        response_json = get_json(response)
        if "error_message" in response_json:
            self._set_transaction_status_text(response_json["error_message"])
        return response_json
