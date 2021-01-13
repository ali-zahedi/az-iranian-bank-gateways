import datetime
import logging
from zeep import Transport, Client

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import SettingDoesNotExist
from azbankgateways.exceptions.exceptions import BankGatewayRejectPayment
from azbankgateways.models import CurrencyEnum, BankType, PaymentStatus

"""
بانک تجارت
"""


class IKC(BaseBank):
    _merchant_code = None
    _sha_1_key = None

    def __init__(self, **kwargs):
        super(IKC, self).__init__(**kwargs)
        self.set_gateway_currency(CurrencyEnum.IRR)
        self._token_api_url = 'https://ikc.shaparak.ir/XToken/Tokens.xml'
        self._payment_url = 'https://ikc.shaparak.ir/TPayment/Payment/index'
        self._verify_api_url = 'https://ikc.shaparak.ir/TVerify/Verify.svc'

    def get_bank_type(self):
        return BankType.TEJARAT_BANK

    def set_default_settings(self):
        for item in ['MERCHANT_CODE', 'SHA_1_KEY', ]:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist()
            setattr(self, f'_{item.lower()}', self.default_setting_kwargs[item])

    def get_pay_data(self):
        data = {
            'amount': str(self.get_gateway_amount()),
            'merchantId': self._merchant_code,
            'invoiceNo': str(self.get_tracking_code()),
            'revertURL': self._get_gateway_callback_url(),
        }
        return data

    def prepare_pay(self):
        super(IKC, self).prepare_pay()

    def pay(self):
        super(IKC, self).pay()
        data = self.get_pay_data()
        client = self._get_client(self._token_api_url)
        result = client.service.MakeToken(**data)
        # MakeTokenResult->token;
        if result.Status == 100:
            token = result.Authority
            self._set_reference_number(token)
        else:
            logging.critical("IKC gateway reject payment")
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    """
    : gateway
    """

    def _get_gateway_payment_method_parameter(self):
        return "POST"

    def _get_gateway_payment_url_parameter(self):
        return self._payment_url

    def _get_gateway_payment_parameter(self):
        params = {
            'token': self.get_reference_number(),
            'merchantId': self._merchant_code,
        }
        return params

    def get_verify_data(self):
        super(IKC, self).get_verify_data()
        data = {
            'token': self.get_reference_number(),
            'merchantId': self._merchant_code,
            'referenceNumber': self.get_reference_number(),
            'sha1Key': self._sha_1_key,
        }
        return data

    def prepare_verify(self, tracking_code):
        super(IKC, self).prepare_verify(tracking_code)

    def verify(self, transaction_code):
        super(IKC, self).verify(transaction_code)
        data = self.get_verify_data()
        client = self._get_client(self._verify_api_url)
        result = client.service.KicccPaymentsVerification(**data)
        if result > 0 or result == self.get_gateway_amount():
            self._set_payment_status(PaymentStatus.COMPLETE)
        else:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
            logging.debug("IKC gateway unapprove payment")

    def prepare_verify_from_gateway(self):
        super(IKC, self).prepare_verify_from_gateway()
        request = self.get_request()
        token = request.POST.get('token', None)
        self._set_reference_number(token)
        self._set_bank_record()
        result = request.POST.get('resultCode', None)
        ref_num = request.POST.get('referenceId', None)
        if str(result) == '100' and ref_num:
            self._set_reference_number(ref_num)
            self._bank.reference_number = ref_num
            extra_information = {
                'token': token,
            }
            self._bank.extra_information = extra_information
            self._bank.save()
        else:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
            logging.debug("IKC gateway cancel.")

    def verify_from_gateway(self, request):
        super(IKC, self).verify_from_gateway(request)

    @staticmethod
    def _get_client(url):
        transport = Transport(timeout=5, operation_timeout=5)
        client = Client(url, transport=transport)
        return client
