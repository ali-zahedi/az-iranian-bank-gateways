import abc
import uuid

import six

from ..exceptions import CurrencyDoesNotSupport, AmountDoesNotSupport
from ..models import Bank, CurrencyEnum


@six.add_metaclass(abc.ABCMeta)
class BaseBank:
    """Base bank for sending to gateway."""
    _gateway_currency: str = CurrencyEnum.IRR
    _currency: str = CurrencyEnum.IRR
    _amount: int = 0
    _gateway_amount: int = 0
    _mobile_number: str = None
    _order_id: int = None

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
            self._gateway_amount = self._amount
        elif self._currency == CurrencyEnum.IRR and self._gateway_currency == CurrencyEnum.IRT:
            self._gateway_amount = CurrencyEnum.rial_to_toman(self._amount)
        elif self._currency == CurrencyEnum.IRT and self._gateway_currency == CurrencyEnum.IRR:
            self._gateway_amount = CurrencyEnum.toman_to_rial(self._amount)
        else:
            self._gateway_amount = self._amount

        if self.get_gateway_amount() < 100:
            raise AmountDoesNotSupport()

    def get_amount(self):
        """get the amount"""
        return self._amount

    def set_amount(self, amount):
        """set amount"""
        if int(amount) <= 0:
            raise AmountDoesNotSupport()
        self._amount = int(amount)

    @abc.abstractmethod
    def prepare_pay(self):
        self.prepare_amount()
        order_id = uuid.uuid4().int
        self._set_order_id(order_id)

    @abc.abstractmethod
    def pay(self):
        self.prepare_pay()

    @abc.abstractmethod
    def prepare_verify(self):
        pass

    @abc.abstractmethod
    def verify(self):
        pass

    def ready(self) -> Bank:
        # TODO: save object and return it
        self.pay()

    def redirect_gateway(self):
        # TODO: redirect to bank
        pass

    def set_mobile_number(self, mobile_number):
        self._mobile_number = mobile_number

    def get_mobile_number(self):
        return self._mobile_number

    def set_callback_url(self, callback):
        # TODO: handle it
        pass

    def _set_reference_number(self, reference_number):
        # reference number get from bank
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

    def get_gateway_amount(self):
        return self._gateway_amount

    def _set_order_id(self, order_id):
        self._order_id = order_id

    def get_order_id(self):
        return self._order_id
