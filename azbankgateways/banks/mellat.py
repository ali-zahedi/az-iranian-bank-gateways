import logging
from json import loads, dumps
from time import strftime, gmtime
from zeep import Transport, Client

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import SettingDoesNotExist
from azbankgateways.exceptions.exceptions import BankGatewayRejectPayment
from azbankgateways.models import CurrencyEnum, BankType, PaymentStatus


class Mellat(BaseBank):
    _terminal_code = None
    _username = None
    _password = None

    def __init__(self, **kwargs):
        super(Mellat, self).__init__(**kwargs)
        self.set_gateway_currency(CurrencyEnum.IRR)
        self._payment_url = 'https://bpm.shaparak.ir/pgwchannel/startpay.mellat'

    def get_bank_type(self):
        return BankType.MELLAT

    def set_default_settings(self):
        for item in ['TERMINAL_CODE', 'USERNAME', 'PASSWORD']:
            if item not in self.default_setting_kwargs:
                raise SettingDoesNotExist()
            setattr(self, f'_{item.lower()}', self.default_setting_kwargs[item])

    """
    gateway
    """
    @classmethod
    def get_minimum_amount(cls):
        return 1000

    def _get_gateway_payment_url_parameter(self):
        return self._payment_url

    def _get_gateway_payment_parameter(self):
        params = {
            'RefId': self.get_reference_number(),
            'MobileNo': self.get_mobile_number()
        }
        return params

    def _get_gateway_payment_method_parameter(self):
        return "GET"

    """
    pay
    """

    def get_pay_data(self):
        description = 'خرید با شماره پیگیری - {}'.format(self.get_tracking_code())
        data = {
            'terminalId': int(self._terminal_code),
            'userName': self._username,
            'userPassword': self._password,
            'orderId': int(self.get_tracking_code()),
            'amount': int(self.get_gateway_amount()),
            'localDate': self._get_current_date(),
            'localTime': self._get_current_time(),
            'additionalData': description,
            'callBackUrl': self._get_gateway_callback_url(),
            'payerId': 0
        }
        return data

    def prepare_pay(self):
        super(Mellat, self).prepare_pay()

    def pay(self):
        super(Mellat, self).pay()

        data = self.get_pay_data()
        client = self._get_client()
        response = client.service.bpPayRequest(**data)
        try:
            status, token = response.split(',')
            if status == '0':
                self._set_reference_number(token)
        except ValueError:
            status_text = 'Unknown error'
            if response == '12':
                status_text = 'Insufficient inventory'
            if response == '21':
                status_text = 'Invalid service'
            if response == '421':
                status_text = 'Invalid IP address'

            self._set_transaction_status_text(status_text)
            logging.critical(status_text)
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    """
    verify from gateway
    """

    def prepare_verify_from_gateway(self):
        super(Mellat, self).prepare_verify_from_gateway()
        post = self.get_request().POST
        token = post.get('RefId', None)
        if not token:
            return
        self._set_reference_number(token)
        self._set_bank_record()
        self._bank.extra_information = dumps(dict(zip(post.keys(), post.values())))
        self._bank.save()

    def verify_from_gateway(self, request):
        super(Mellat, self).verify_from_gateway(request)

    """
    verify
    """

    def get_verify_data(self):
        super(Mellat, self).get_verify_data()
        data = {
            'terminalId': self._terminal_code,
            'userName': self._username,
            'userPassword': self._password,
            'orderId': self.get_tracking_code(),
            'saleOrderId': self.get_tracking_code(),
            'saleReferenceId': self._get_sale_reference_id()
        }
        return data

    def prepare_verify(self, tracking_code):
        super(Mellat, self).prepare_verify(tracking_code)

    def verify(self, transaction_code):
        super(Mellat, self).verify(transaction_code)
        data = self.get_verify_data()
        client = self._get_client()

        verify_result = client.service.bpVerifyRequest(**data)
        if verify_result == "0":
            self._settle_transaction()
        else:
            verify_result = client.service.bpInquiryRequest(**data)
            if verify_result == "0":
                self._settle_transaction()
            else:
                logging.debug(
                    "Not able to verify the transaction, Making reversal request"
                )
                reversal_result = client.service.bpReversalRequest(**data)

                if reversal_result != "0":
                    logging.debug("Reversal request was not successfull")

                self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
                logging.debug("Mellat gateway unapproved the payment")

    def _settle_transaction(self):
        data = self.get_verify_data()
        client = self._get_client()
        settle_result = client.service.bpSettleRequest(**data)
        if settle_result == "0":
            self._set_payment_status(PaymentStatus.COMPLETE)
        else:
            logging.debug("Mellat gateway did not settle the payment")

    @staticmethod
    def _get_client():
        transport = Transport(timeout=5, operation_timeout=5)
        client = Client('https://bpm.shaparak.ir/pgwchannel/services/pgw?wsdl', transport=transport)
        return client

    @staticmethod
    def _get_current_time():
        return strftime("%H%M%S")

    @staticmethod
    def _get_current_date():
        return strftime("%Y%m%d", gmtime())

    def _get_sale_reference_id(self):
        extra_information = loads(getattr(self._bank, 'extra_information', '{}'))
        return extra_information.get('SaleReferenceId', '1')
