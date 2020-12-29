import logging
import base64
import datetime

import requests
from Crypto.Cipher import DES3
from zeep import Transport, Client

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import SettingDoesNotExist, BankGatewayConnectionError
from azbankgateways.exceptions.exceptions import BankGatewayRejectPayment
from azbankgateways.models import CurrencyEnum, BankType, PaymentStatus
from azbankgateways.utils import get_json


class SEP(BaseBank):
    _merchant_code = None
    _terminal_code = None

    def __init__(self, **kwargs):
        super(SEP, self).__init__(**kwargs)
        self.set_gateway_currency(CurrencyEnum.IRR)
        self._token_api_url = 'https://sep.shaparak.ir/MobilePG/MobilePayment'
        self._payment_url = 'https://sep.shaparak.ir/OnlinePG/OnlinePG'
        self._verify_api_url = 'https://verify.sep.ir/Payments/ReferencePayment.asmx?WSDL'

    def get_bank_type(self):
        return BankType.SEP

    def set_default_settings(self):
        for item in ['MERCHANT_CODE', 'TERMINAL_CODE']:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist()
            setattr(self, f'_{item.lower()}', self.default_setting_kwargs[item])

    def get_pay_data(self):
        data = {
            'Action': 'Token',
            'Amount': self.get_gateway_amount(),
            'Wage': 0,
            'TerminalId': self._merchant_code,
            'ResNum': self.get_tracking_code(),
            'RedirectURL': self._get_gateway_callback_url(),
            'CellNumber': self.get_mobile_number(),
        }
        return data

    def prepare_pay(self):
        super(SEP, self).prepare_pay()

    def pay(self):
        super(SEP, self).pay()
        data = self.get_pay_data()
        response_json = self._send_data(self._token_api_url, data)
        if str(response_json['status']) == '1':
            token = response_json['token']
            self._set_reference_number(token)
        else:
            logging.critical("SEP gateway reject payment")
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    """
    : gateway
    """
    def _get_gateway_payment_url_parameter(self):
        return self._payment_url

    def _get_gateway_payment_method_parameter(self):
        return 'POST'

    def _get_gateway_payment_parameter(self):
        params = {
            'Token': self.get_reference_number(),
            'GetMethod': 'true',
        }
        return params

    """
    verify from gateway
    """
    def prepare_verify_from_gateway(self):
        super(SEP, self).prepare_verify_from_gateway()
        request = self.get_request()
        tracking_code = request.GET.get('ResNum', None)
        token = request.GET.get('Token', None)
        self._set_tracking_code(tracking_code)
        self._set_bank_record()
        ref_num = request.GET.get('RefNum', None)
        if request.GET.get('State', 'NOK') == 'OK' and ref_num:
            self._set_reference_number(ref_num)
            self._bank.reference_number = ref_num
            extra_information = f"TRACENO={request.GET.get('TRACENO', None)}, RefNum={ref_num}, Token={token}"
            self._bank.extra_information = extra_information
            self._bank.save()

    def verify_from_gateway(self, request):
        super(SEP, self).verify_from_gateway(request)

    """
    verify
    """
    def get_verify_data(self):
        super(SEP, self).get_verify_data()
        data = self.get_reference_number(), self._merchant_code
        return data

    def prepare_verify(self, tracking_code):
        super(SEP, self).prepare_verify(tracking_code)

    def verify(self, transaction_code):
        super(SEP, self).verify(transaction_code)
        data = self.get_verify_data()
        client = self._get_client(self._verify_api_url)
        result = client.service.verifyTransaction(
            *data
        )
        if result == self.get_gateway_amount():
            self._set_payment_status(PaymentStatus.COMPLETE)
        else:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
            logging.debug("SEP gateway unapprove payment")

    def _send_data(self, api, data):
        try:
            response = requests.post(api, json=data, timeout=5)
        except requests.Timeout:
            logging.exception("SEP time out gateway {}".format(data))
            raise BankGatewayConnectionError()
        except requests.ConnectionError:
            logging.exception("SEP time out gateway {}".format(data))
            raise BankGatewayConnectionError()

        response_json = get_json(response)
        self._set_transaction_status_text(response_json.get('errorDesc'))
        return response_json

    @staticmethod
    def _get_client(url):
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0',
        }
        transport = Transport(timeout=5, operation_timeout=5)
        transport.session.headers = headers
        client = Client(url, transport=transport)
        return client
