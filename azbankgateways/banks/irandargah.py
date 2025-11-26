import logging

import requests

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import SettingDoesNotExist
from azbankgateways.exceptions.exceptions import (
    BankGatewayConnectionError,
    BankGatewayRejectPayment,
)
from azbankgateways.models import BankType, CurrencyEnum, PaymentStatus
from azbankgateways.utils import get_json


class IranDargah(BaseBank):
    _merchant_code = None
    _sandbox = False

    def __init__(self, **kwargs):
        kwargs.setdefault("SANDBOX", 0)
        super().__init__(**kwargs)
        self.set_gateway_currency(CurrencyEnum.IRR)
        self._sandbox = kwargs.get("SANDBOX", 0) == 1

        base_url = "https://dargaah.ir"
        if self._sandbox:
            base_url += "/sandbox"

        self._payment_url = f"{base_url}/payment"
        self._startpay_url = f"{base_url}/ird/startpay/"
        self._verify_url = f"{base_url}/verification"

    def get_bank_type(self):
        return BankType.IRANDARGAH

    def set_default_settings(self):
        for item in ["MERCHANT_CODE"]:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist(f"{item} not in settings")
            setattr(self, f"_{item.lower()}", self.default_setting_kwargs[item])

    def _get_gateway_payment_url_parameter(self):
        return f"{self._startpay_url}{self.get_reference_number()}"

    def _get_gateway_payment_parameter(self):
        return {}

    def _get_gateway_payment_method_parameter(self):
        return "GET"

    def get_pay_data(self):
        return {
            "merchantID": self._merchant_code,
            "amount": self.get_gateway_amount(),
            "callbackURL": self._get_gateway_callback_url(),
            "orderId": str(self.get_tracking_code()),
            **self.get_custom_data(),
        }

    def prepare_pay(self):
        super().prepare_pay()

    def pay(self):
        super().pay()
        data = self.get_pay_data()
        result = self._send_data(api=self._payment_url, data=data)
        if result["status"] == 200:
            self._set_reference_number(result["authority"])
        else:
            logging.critical("IranDargah reject payment: %s", result.get("message"))
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    def prepare_verify_from_gateway(self):
        super().prepare_verify_from_gateway()
        authority = self.get_request().POST.get("authority")
        self._set_reference_number(authority)
        self._set_bank_record()

    def verify_from_gateway(self, request):
        super().verify_from_gateway(request)

    def get_verify_data(self):
        return {
            "merchantID": self._merchant_code,
            "authority": self.get_reference_number(),
            "amount": self.get_gateway_amount(),
            "orderId": str(self.get_tracking_code()),
        }

    def prepare_verify(self, tracking_code):
        super().prepare_verify(tracking_code)

    def verify(self, transaction_code):
        super().verify(transaction_code)
        data = self.get_verify_data()
        result = self._send_data(api=self._verify_url, data=data)

        if result.get("status") in [100, 101]:
            self._set_payment_status(PaymentStatus.COMPLETE)
        else:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
            logging.debug("IranDargah verify failed: %s", result.get("message"))

    def _send_data(self, api, data):
        try:
            response = requests.post(api, json=data, timeout=self.get_timeout())
            response.raise_for_status()
        except requests.RequestException as e:
            logging.exception("IranDargah connection error: %s", e)
            raise BankGatewayConnectionError()

        result = get_json(response)
        msg = result.get("message", "no message")
        self._set_transaction_status_text(msg)
        return result
