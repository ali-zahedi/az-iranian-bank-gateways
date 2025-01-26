import logging

import requests

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import SettingDoesNotExist
from azbankgateways.exceptions.exceptions import BankGatewayRejectPayment, BankGatewayConnectionError
from azbankgateways.models import BankType, CurrencyEnum, PaymentStatus
from azbankgateways.utils import get_json


class ZarinpalV4(BaseBank):
    _merchant_code = None
    _sandbox = None

    def __init__(self, **kwargs):
        kwargs.setdefault("SANDBOX", 0)
        super(ZarinpalV4, self).__init__(**kwargs)
        self.set_gateway_currency(CurrencyEnum.IRT)
        self._payment_type = 'payment'
        if self._sandbox:
            self._payment_type = 'sandbox'
        self._payment_url = f"https://{self._payment_type}.zarinpal.com/pg/v4/payment/request.json"
        self._startpay_url = "https://{}.zarinpal.com/pg/StartPay/{}"
        self._verify_url = f"https://{self._payment_type}.zarinpal.com/pg/v4/payment/verify.json"

    def get_bank_type(self):
        return BankType.ZARINPALV4

    def set_default_settings(self):
        for item in ["MERCHANT_CODE", "SANDBOX"]:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist(f"{item} does not exist in default_setting_kwargs")
            setattr(self, f"_{item.lower()}", self.default_setting_kwargs[item])

    """
    gateway
    """

    @classmethod
    def get_minimum_amount(cls):
        return 1000

    def _get_gateway_payment_url_parameter(self):
        return self._startpay_url.format(self._payment_type, self.get_reference_number())

    def _get_gateway_payment_parameter(self):
        return {}

    def _get_gateway_payment_method_parameter(self):
        return "GET"

    """
    pay
    """

    def get_pay_data(self):
        description = "خرید با شماره پیگیری - {}".format(self.get_tracking_code())

        data = {
            "description": description,
            "merchant_id": self._merchant_code,
            "amount": self.get_gateway_amount(),
            "currency": self._currency,
            "metadata": {

            },
            "callback_url": self._get_gateway_callback_url(),
        }
        mobile_number = self.get_mobile_number()
        if mobile_number:
            data["metadata"].update({"mobile": mobile_number})
        data.update(self.get_custom_data())
        return data

    def prepare_pay(self):
        super(ZarinpalV4, self).prepare_pay()

    def pay(self):
        super(ZarinpalV4, self).pay()
        data = self.get_pay_data()
        result = self._send_data(api=self._payment_url, data=data)
        if result['data']:
            token = result['data']['authority']
            self._set_reference_number(token)
        else:
            logging.critical("ZarinpalV4 gateway reject payment")
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    """
    verify from gateway
    """

    def prepare_verify_from_gateway(self):
        super(ZarinpalV4, self).prepare_verify_from_gateway()
        token = self.get_request().GET.get("Authority", None)
        self._set_reference_number(token)
        self._set_bank_record()

    def verify_from_gateway(self, request):
        super(ZarinpalV4, self).verify_from_gateway(request)

    """
    verify
    """

    def get_verify_data(self):
        super(ZarinpalV4, self).get_verify_data()
        return {
            "merchant_id": self._merchant_code,
            "authority": self.get_reference_number(),
            "amount": self.get_gateway_amount(),
        }

    def prepare_verify(self, tracking_code):
        super(ZarinpalV4, self).prepare_verify(tracking_code)

    def verify(self, transaction_code):
        super(ZarinpalV4, self).verify(transaction_code)
        data = self.get_verify_data()
        result = self._send_data(api=self._verify_url, data=data)
        if result['data'] and result['data']['code'] in [100, 101]:
            self._set_payment_status(PaymentStatus.COMPLETE)
        else:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
            logging.debug("ZarinpalV4 gateway unapprove payment")

    def _send_data(self, api, data):
        try:
            response = requests.post(api, json=data, timeout=5)
        except requests.Timeout:
            logging.exception("ZARINPALV4 time out gateway {}".format(data))
            raise BankGatewayConnectionError()
        except requests.ConnectionError:
            logging.exception("ZARINPALV4 time out gateway {}".format(data))
            raise BankGatewayConnectionError()

        response_json = get_json(response)
        if response_json['data']:
            self._set_transaction_status_text(response_json['data']['message'])
        else:
            self._set_transaction_status_text(response_json['errors']['message'])
        return response_json
