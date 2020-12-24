import json
import logging

import requests

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import SettingDoesNotExist, BankGatewayConnectionError
from azbankgateways.exceptions.exceptions import BankGatewayRejectPayment
from azbankgateways.models import CurrencyEnum, BankType, PaymentStatus
from azbankgateways.utils import get_json


class Zibal(BaseBank):
    _merchant_code = None

    def __init__(self, **kwargs):
        super(Zibal, self).__init__(**kwargs)
        self.set_gateway_currency(CurrencyEnum.IRR)
        self._token_api_url = 'https://gateway.zibal.ir/v1/request'
        self._payment_url = 'https://gateway.zibal.ir/start/{}'
        self._verify_api_url = 'https://gateway.zibal.ir/v1/verify'

    def get_bank_type(self):
        return BankType.ZIBAL

    def set_default_settings(self):
        for item in ['MERCHANT_CODE']:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist()
            setattr(self, f'_{item.lower()}', self.default_setting_kwargs[item])

    """
    gateway
    """

    def _get_gateway_payment_url_parameter(self):
        return self._payment_url.format(self.get_reference_number())

    def _get_gateway_payment_parameter(self):
        params = {}
        return params

    def _get_gateway_payment_method_parameter(self):
        return "GET"

    """
    pay
    """

    def get_pay_data(self):
        data = {
            'merchant': self._merchant_code,
            'amount': self.get_gateway_amount(),
            'callbackUrl': self._get_gateway_callback_url(),
            'orderId': self.get_tracking_code(),
            'mobile': self.get_mobile_number(),
        }
        return data

    def prepare_pay(self):
        super(Zibal, self).prepare_pay()

    def pay(self):
        super(Zibal, self).pay()
        data = self.get_pay_data()
        response_json = self._send_data(self._token_api_url, data)
        if response_json['result'] == 100:
            token = response_json['trackId']
            self._set_reference_number(token)
        else:
            logging.critical("Zibal gateway reject payment")
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    """
    verify from gateway
    """

    def prepare_verify_from_gateway(self):
        super(Zibal, self).prepare_verify_from_gateway()
        token = self.get_request().GET.get('trackId', None)
        self._set_reference_number(token)
        self._set_bank_record()

    def verify_from_gateway(self, request):
        super(Zibal, self).verify_from_gateway(request)

    """
    verify
    """

    def get_verify_data(self):
        super(Zibal, self).get_verify_data()
        data = {
            'trackId': self.get_reference_number(),
            'merchant': self._merchant_code,
        }
        return data

    def prepare_verify(self, tracking_code):
        super(Zibal, self).prepare_verify(tracking_code)

    def verify(self, transaction_code):
        super(Zibal, self).verify(transaction_code)
        data = self.get_verify_data()
        response_json = self._send_data(self._verify_api_url, data)
        if response_json['result'] == 100 and response_json['status'] == 1:
            self._set_payment_status(PaymentStatus.COMPLETE)
            extra_information = json.dumps(response_json)
            self._bank.extra_information = extra_information
            self._bank.save()
        else:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
            logging.debug("Zibal gateway unapprove payment")

    def _send_data(self, api, data):
        try:
            response = requests.post(api, json=data, timeout=5)
        except requests.Timeout:
            logging.exception("Zibal time out gateway {}".format(data))
            raise BankGatewayConnectionError()
        except requests.ConnectionError:
            logging.exception("Zibal time out gateway {}".format(data))
            raise BankGatewayConnectionError()

        response_json = get_json(response)
        self._set_transaction_status_text(response_json['message'])
        return response_json
