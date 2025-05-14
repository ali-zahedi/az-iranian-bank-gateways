from __future__ import annotations

import json
import logging

import requests

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import BankGatewayConnectionError
from azbankgateways.exceptions import SettingDoesNotExist
from azbankgateways.exceptions.exceptions import BankGatewayRejectPayment
from azbankgateways.models import BankType
from azbankgateways.models import CurrencyEnum
from azbankgateways.models import PaymentStatus
from azbankgateways.utils import get_json
from azbankgateways.utils import split_to_dict_querystring


class IDPay(BaseBank):
    _merchant_code = None
    _method = None
    _x_sandbox = None
    _payment_url = None
    _params: dict = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_gateway_currency(CurrencyEnum.IRR)
        self._token_api_url = "https://api.idpay.ir/v1.1/payment"
        self._verify_api_url = "https://api.idpay.ir/v1.1/payment/verify"

    def get_bank_type(self):
        return BankType.IDPAY

    def set_default_settings(self):
        for item in ["MERCHANT_CODE", "METHOD", "X_SANDBOX"]:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist()
            setattr(self, f"_{item.lower()}", self.default_setting_kwargs[item])

        self._x_sandbox = str(self._x_sandbox)

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
        super().prepare_pay()

    def pay(self):
        super().pay()
        data = self.get_pay_data()
        response_json = self._send_data(self._token_api_url, data)
        if "id" in response_json and "link" in response_json and response_json["link"] and response_json["id"]:
            token = response_json["id"]
            self._payment_url, self._params = split_to_dict_querystring(response_json["link"])
            self._set_reference_number(token)
        else:
            logging.critical("IDPay gateway reject payment")
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    """
    verify gateway
    """

    def prepare_verify_from_gateway(self):
        super().prepare_verify_from_gateway()
        for method in ["GET", "POST", "data"]:
            token = getattr(self.get_request(), method).get("id", None)
            if token:
                self._set_reference_number(token)
                self._set_bank_record()
                break

    def verify_from_gateway(self, request):
        super().verify_from_gateway(request)

    """
    verify
    """

    def get_verify_data(self):
        super().get_verify_data()
        data = {
            "id": self.get_reference_number(),
            "order_id": self.get_tracking_code(),
        }
        return data

    def prepare_verify(self, tracking_code):
        super().prepare_verify(tracking_code)

    def verify(self, transaction_code):
        super().verify(transaction_code)
        data = self.get_verify_data()
        response_json = self._send_data(self._verify_api_url, data, timeout=10)
        if response_json.get("verify", {}).get("date", None):
            self._set_payment_status(PaymentStatus.COMPLETE)
            extra_information = json.dumps(response_json)
            self._bank.extra_information = extra_information
            self._bank.save()
        else:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
            logging.debug("IDPay gateway unapprove payment")

    def _send_data(self, api, data, timeout=5):
        headers = {
            "X-API-KEY": self._merchant_code,
            "X-SANDBOX": self._x_sandbox,
        }
        try:
            response = requests.post(api, headers=headers, json=data, timeout=timeout)
        except requests.Timeout:
            logging.exception(f"IDPay time out gateway {data}")
            raise BankGatewayConnectionError() from None
        except requests.ConnectionError:
            logging.exception(f"IDPay time out gateway {data}")
            raise BankGatewayConnectionError() from None

        response_json = get_json(response)
        if "error_message" in response_json:
            self._set_transaction_status_text(response_json["error_message"])
        return response_json
