import abc

import six

from ..exceptions import CurrencyDoesNotSupport
from ..models import Bank, CurrencyEnum


@six.add_metaclass(abc.ABCMeta)
class BaseBank:
    """Base bank for sending to gateway."""
    _gateway_currency = CurrencyEnum.IRR
    _currency = CurrencyEnum.IRR
    _amount = 0

    def __init__(self, **kwargs):
        self.default_setting_kwargs = kwargs
        self.set_default_settings()

    @abc.abstractmethod
    def set_default_settings(self):
        """default setting, like fetch merchant code, terminal id and etc"""
        pass

    def prepare_amount(self):
        """prepare amount"""
        if self._currency == self._gateway_currency:
            return self._amount
        elif self._currency == CurrencyEnum.IRR and self._gateway_currency == CurrencyEnum.IRT:
            return CurrencyEnum.rial_to_toman(self._amount)
        elif self._currency == CurrencyEnum.IRT and self._gateway_currency == CurrencyEnum.IRR:
            return CurrencyEnum.toman_to_rial(self._amount)

        return self._amount

    def get_amount(self):
        """get the amount"""
        return self._amount

    def set_amount(self, amount):
        """set the amount"""
        self._amount = int(amount)

    @abc.abstractmethod
    def prepare_pay(self):
        pass

    @abc.abstractmethod
    def pay(self):
        pass

    @abc.abstractmethod
    def prepare_verify(self):
        pass

    @abc.abstractmethod
    def verify(self):
        pass

    def ready(self) -> Bank:
        # TODO: save object and return it
        self.pay()

    def redirect(self):
        # TODO: redirect to bank
        pass

    def set_mobile_number(self, mobile_number):
        # TODO: handle mobile number
        pass

    def set_callback_url(self, callback):
        # TODO: handle it
        pass

    def set_reference_number(self):
        pass

    def get_reference_number(self):
        pass

    def get_tracking_code(self):
        # TODO: handle it
        pass

    def get_transaction_status_text(self):
        # TODO: handle it
        pass

    def set_gateway_currency(self, currency: CurrencyEnum):
        if currency not in [CurrencyEnum.IRR, CurrencyEnum.IRT]:
            raise CurrencyDoesNotSupport()
        self._gateway_currency = currency

    def get_gateway_currency(self):
        return self._gateway_currency

    def set_currency(self, currency: CurrencyEnum):
        if currency not in [CurrencyEnum.IRR, CurrencyEnum.IRT]:
            raise CurrencyDoesNotSupport()
        self._currency = currency

    def get_currency(self):
        return self._currency
