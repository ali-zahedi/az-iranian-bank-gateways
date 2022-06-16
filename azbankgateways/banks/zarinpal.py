import logging

from zeep import Transport, Client

from azbankgateways.banks import BaseBank
from azbankgateways.exceptions import SettingDoesNotExist
from azbankgateways.exceptions.exceptions import BankGatewayRejectPayment
from azbankgateways.models import CurrencyEnum, BankType, PaymentStatus


class Zarinpal(BaseBank):
    _merchant_code = None
    _sandbox = None

    def __init__(self, **kwargs):
        super(Zarinpal, self).__init__(**kwargs)
        self.set_gateway_currency(CurrencyEnum.IRT)
        self._payment_url = 'https://www.zarinpal.com/pg/StartPay/{}/ZarinGate'
        self._sandbox_url = 'https://sandbox.zarinpal.com/pg/StartPay/{}/ZarinGate'

    def get_bank_type(self):
        return BankType.ZARINPAL

    def set_default_settings(self):
        for item in ['MERCHANT_CODE', 'SANDBOX']:
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
        if self._sandbox:
            return self._sandbox_url.format(self.get_reference_number())
        return self._payment_url.format(self.get_reference_number())

    def _get_gateway_payment_parameter(self):
        return {

        }

    def _get_gateway_payment_method_parameter(self):
        return "GET"

    """
    pay
    """

    def get_pay_data(self):
        description = 'خرید با شماره پیگیری - {}'.format(self.get_tracking_code())

        return {
            'Description': description,
            'MerchantID': self._merchant_code,
            'Amount': self.get_gateway_amount(),
            'Email': None,
            'Mobile': self.get_mobile_number(),
            'CallbackURL': self._get_gateway_callback_url(),
        }

    def prepare_pay(self):
        super(Zarinpal, self).prepare_pay()

    def pay(self):
        super(Zarinpal, self).pay()
        data = self.get_pay_data()
        client = self._get_client()
        result = client.service.PaymentRequest(**data)
        if result.Status == 100:
            token = result.Authority
            self._set_reference_number(token)
        else:
            logging.critical("Zarinpal gateway reject payment")
            raise BankGatewayRejectPayment(self.get_transaction_status_text())

    """
    verify from gateway
    """

    def prepare_verify_from_gateway(self):
        super(Zarinpal, self).prepare_verify_from_gateway()
        token = self.get_request().GET.get('Authority', None)
        self._set_reference_number(token)
        self._set_bank_record()

    def verify_from_gateway(self, request):
        super(Zarinpal, self).verify_from_gateway(request)

    """
    verify
    """

    def get_verify_data(self):
        super(Zarinpal, self).get_verify_data()
        return {
            'MerchantID': self._merchant_code,
            'Authority': self.get_reference_number(),
            'Amount': self.get_gateway_amount()
        }

    def prepare_verify(self, tracking_code):
        super(Zarinpal, self).prepare_verify(tracking_code)

    def verify(self, transaction_code):
        super(Zarinpal, self).verify(transaction_code)
        data = self.get_verify_data()
        client = self._get_client(timeout=10)
        result = client.service.PaymentVerification(**data)
        if result.Status in [100, 101]:
            self._set_payment_status(PaymentStatus.COMPLETE)
        else:
            self._set_payment_status(PaymentStatus.CANCEL_BY_USER)
            logging.debug("Zarinpal gateway unapprove payment")

    def _get_client(self, timeout=5):
        transport = Transport(timeout=timeout, operation_timeout=timeout)
        if self._sandbox:
            return Client(
                'https://sandbox.zarinpal.com/pg/services/WebGate/wsdl',
                transport=transport,
            )

        return Client(
            'https://www.zarinpal.com/pg/services/WebGate/wsdl',
            transport=transport,
        )
