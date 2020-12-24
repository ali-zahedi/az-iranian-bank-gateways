import json
import logging

import requests

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import SettingDoesNotExist, BankGatewayConnectionError
from azbankgateways.exceptions.exceptions import BankGatewayRejectPayment
from azbankgateways.models import CurrencyEnum, BankType, PaymentStatus
from azbankgateways.utils import get_json, append_querystring, split_to_dict_querystring


class Bahamta(BaseBank):
    _merchant_code = None
    _params = {}

    def __init__(self, **kwargs):
        super(Bahamta, self).__init__(**kwargs)
        self.set_gateway_currency(CurrencyEnum.IRR)
        self._token_api_url = 'https://webpay.bahamta.com/api/create_request'
        self._payment_url = None
        self._verify_api_url = 'https://webpay.bahamta.com/api/confirm_payment'

    def get_bank_type(self):
        return BankType.BAHAMTA

    def set_default_settings(self):
        for item in ['MERCHANT_CODE']:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist()
            setattr(self, f'_{item.lower()}', self.default_setting_kwargs[item])

    """
    Gateway
    """
    def _get_gateway_payment_url_parameter(self):
        return self._payment_url

    def _get_gateway_payment_parameter(self):
        params = {
        }
        params.update(self._params)
        return params

    def _get_gateway_payment_method_parameter(self):
        return "GET"

    """
    pay
    """
    def get_pay_data(self):
        data = {
            'api_key': self._merchant_code,
            'reference': self.get_tracking_code(),
            'amount_irr': self.get_gateway_amount(),
            'payer_mobile': self.get_mobile_number(),
            'callback_url': self._get_gateway_callback_url(),
        }
        return data

    def prepare_pay(self):
        super(Bahamta, self).prepare_pay()

    def pay(self):
        super(Bahamta, self).pay()
        data = self.get_pay_data()
        response_json = self._send_data(self._token_api_url, data)
        if response_json['ok']:
            # در این سیستم رفرنس برای ذخیره سازی بر نمی گردد!
            token = self.get_tracking_code()
            self._payment_url, self._params = split_to_dict_querystring(response_json['result']['payment_url'])
            self._set_reference_number(token)
        else:
            logging.critical("Bahamta gateway reject payment")
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    """
    verify gateway    
    """
    def prepare_verify_from_gateway(self):
        super(Bahamta, self).prepare_verify_from_gateway()
        token = self.get_request().GET.get('reference', None)
        self._set_reference_number(token)
        self._set_bank_record()

    def verify_from_gateway(self, request):
        super(Bahamta, self).verify_from_gateway(request)

    """
    verify
    """
    def get_verify_data(self):
        super(Bahamta, self).get_verify_data()
        data = {
            'api_key': self._merchant_code,
            'reference': self.get_reference_number(),
            'amount_irr': self.get_gateway_amount(),
        }
        return data

    def prepare_verify(self, tracking_code):
        super(Bahamta, self).prepare_verify(tracking_code)

    def verify(self, transaction_code):
        super(Bahamta, self).verify(transaction_code)
        data = self.get_verify_data()
        response_json = self._send_data(self._verify_api_url, data)
        if response_json.get('ok', False) and response_json.get('result', {}).get('state', None) == 'paid':
            self._set_payment_status(PaymentStatus.COMPLETE)
            extra_information = json.dumps(response_json.get('result', {}))
            self._bank.extra_information = extra_information
            self._bank.save()
        else:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
            logging.debug("Bahamta gateway unapprove payment")

    def _send_data(self, api, data):
        try:
            url = append_querystring(api, data)
            response = requests.get(url, timeout=5)
        except requests.Timeout:
            logging.exception("Bahamta time out gateway {}".format(data))
            raise BankGatewayConnectionError()
        except requests.ConnectionError:
            logging.exception("Bahamta time out gateway {}".format(data))
            raise BankGatewayConnectionError()

        response_json = get_json(response)
        self._set_transaction_status_text(response_json.get('error'))
        return response_json
