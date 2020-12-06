import logging
import base64
import datetime

import requests
from Crypto.Cipher import DES3

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import SettingDoesNotExist, BankGatewayConnectionError
from azbankgateways.exceptions.exceptions import BankGatewayRejectPayment
from azbankgateways.models import CurrencyEnum, BankType, PaymentStatus
from azbankgateways.utils import get_json


class BMI(BaseBank):
    merchant_code = None
    terminal_code = None
    secret_key = None

    def __init__(self, **kwargs):
        super(BMI, self).__init__(**kwargs)
        self.set_gateway_currency(CurrencyEnum.IRR)
        self._token_api_url = 'https://sadad.shaparak.ir/vpg/api/v0/Request/PaymentRequest'
        self._payment_url = "https://sadad.shaparak.ir/VPG/Purchase?Token={}"
        self._verify_api_url = 'https://sadad.shaparak.ir/vpg/api/v0/Advice/Verify'

    def prepare_pay(self):
        super(BMI, self).prepare_pay()

    def get_pay_data(self):
        time_now = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S %P')
        data = {
            'TerminalId': self.terminal_code,
            'MerchantId': self.merchant_code,
            'Amount': self.get_gateway_amount(),
            'SignData': self._encrypt_des3(
                '{};{};{}'.format(
                    self.terminal_code,
                    self.get_order_id(),
                    self.get_gateway_amount(),
                )
            ),
            'ReturnUrl': 'https://google.com',
            'LocalDateTime': time_now,
            'OrderId': self.get_order_id(),
            'AdditionalData': 'oi:%s-ou:%s' % (self.get_order_id(), self.get_mobile_number()),
        }
        return data

    def pay(self):
        super(BMI, self).pay()
        data = self.get_pay_data()
        try:
            response = requests.post(self._token_api_url, json=data, timeout=5)
        except requests.Timeout:
            logging.exception("BMI time out gateway {}".format(data))
            raise BankGatewayConnectionError()
        except requests.ConnectionError:
            logging.exception("BMI time out gateway {}".format(data))
            raise BankGatewayConnectionError()

        response_json = get_json(response)
        self._set_transaction_status_text(response_json['Description'])
        if response_json['ResCode'] == '0':
            token = response_json['Token']
            self._set_reference_number(token)
        else:
            logging.critical("BMI gateway reject payment")
            raise BankGatewayRejectPayment()

    def get_gateway_payment_url(self):
        return self._payment_url.format(self.get_reference_number())

    def prepare_verify(self):
        pass

    def verify(self):
        pass

    def get_bank_type(self):
        return BankType.BMI

    def set_default_settings(self):
        for item in ['MERCHANT_CODE', 'TERMINAL_CODE', 'SECRET_KEY']:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist()
            setattr(self, item.lower(), self.default_setting_kwargs[item])

    @classmethod
    def _pad(cls, text, pad_size=16):
        text_length = len(text)
        last_block_size = text_length % pad_size
        remaining_space = pad_size - last_block_size
        text = text + (remaining_space * chr(remaining_space))
        return text

    def _encrypt_des3(self, text):
        secret_key_bytes = base64.b64decode(self.secret_key)
        text = self._pad(text, 8)
        cipher = DES3.new(secret_key_bytes, DES3.MODE_ECB)
        cipher_text = cipher.encrypt(str.encode(text))
        return base64.b64encode(cipher_text).decode("utf-8")
