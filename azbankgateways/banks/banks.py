import abc
import logging
import uuid
import datetime

import six
from django.shortcuts import redirect

from ..exceptions import CurrencyDoesNotSupport, AmountDoesNotSupport, BankGatewayTokenExpired, BankGatewayStateInvalid
from ..models import Bank, CurrencyEnum, PaymentStatus
from .. import default_settings as settings


@six.add_metaclass(abc.ABCMeta)
class BaseBank:
    """Base bank for sending to gateway."""
    _gateway_currency: str = CurrencyEnum.IRR
    _currency: str = CurrencyEnum.IRR
    _amount: int = 0
    _gateway_amount: int = 0
    _mobile_number: str = None
    _order_id: int = None
    _reference_number: str = ''
    _transaction_status_text: str = ''
    _client_callback_url: str = ''
    _bank: Bank = None

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

        if self.get_gateway_amount() < 1000:
            raise AmountDoesNotSupport()

    @abc.abstractmethod
    def get_bank_type(self):
        pass

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
        logging.debug("Prepare pay method")
        self.prepare_amount()
        order_id = int(str(uuid.uuid4().int)[-1 * settings.ORDER_CODE_LENGTH:])
        self._set_order_id(order_id)

    @abc.abstractmethod
    def get_pay_data(self):
        pass

    @abc.abstractmethod
    def pay(self):
        logging.debug("Pay method")
        self.prepare_pay()

    @abc.abstractmethod
    def prepare_verify(self):
        pass

    @abc.abstractmethod
    def verify(self):
        pass

    def ready(self) -> Bank:
        self.pay()
        bank = Bank.objects.create(
            bank_type=self.get_bank_type(),
            amount=self.get_amount(),
            reference_number=self.get_reference_number(),
            response_result=self.get_transaction_status_text(),
            order_id=self.get_order_id(),
        )
        self._bank = bank
        self._set_payment_status(PaymentStatus.WAITING)
        if self._client_callback_url:
            self.set_callback_url(self._client_callback_url)
        return bank

    @abc.abstractmethod
    def prepare_verify_from_gateway(self, request):
        pass

    def verify_from_gateway(self, request):
        self.prepare_verify_from_gateway(request)
        self._set_payment_status(PaymentStatus.RETURN_FROM_BANK)
        self.verify()

    @abc.abstractmethod
    def get_gateway_payment_url(self):
        pass

    def redirect_gateway(self):
        if (datetime.datetime.now() - self._bank.created_at).seconds > 120:
            self._set_payment_status(PaymentStatus.EXPIRE_GATEWAY_TOKEN)
            logging.debug("Redirect to bank expire!")
            raise BankGatewayTokenExpired()
        logging.debug("Redirect to bank")
        self._set_payment_status(PaymentStatus.REDIRECT_TO_BANK)
        return redirect(self.get_gateway_payment_url())

    def set_mobile_number(self, mobile_number):
        self._mobile_number = mobile_number

    def get_mobile_number(self):
        return self._mobile_number

    def set_callback_url(self, callback_url):

        if self._bank and self._bank.status != PaymentStatus.WAITING:
            logging.critical(
                "You are change the call back url in invalid situation.",
                extra={
                    'bank_id': self._bank.pk,
                    'status': self._bank.status,
                }
            )
            raise BankGatewayStateInvalid(
                'Bank state not equal to waiting. Probably finish or redirect to bank gateway. status is {}'.format(
                    self._bank.status
                )
            )

        if self._bank.status == PaymentStatus.WAITING:
            self._bank.callback_url = callback_url
            self._bank.save()
        else:
            self._client_callback_url = callback_url

    def _set_reference_number(self, reference_number):
        """reference number get from bank """
        self._reference_number = reference_number

    def set_bank_record(self):
        try:
            self._bank = Bank.objects.get(reference_number=self.get_reference_number(), bank_type=self.get_bank_type())
            logging.debug("Set reference find bank object.")
        except Bank.DoesNotExist:
            logging.debug("Cant find bank record object.")
            raise BankGatewayStateInvalid(
                "Cant find bank record with reference number reference number is {}".format(
                    self.get_reference_number()
                )
            )

    def get_reference_number(self):
        return self._reference_number

    def get_tracking_code(self):
        # TODO: handle it
        pass

    def _set_transaction_status_text(self, txt):
        self._transaction_status_text = txt

    def get_transaction_status_text(self):
        return self._transaction_status_text

    def _set_payment_status(self, payment_status):
        if payment_status == PaymentStatus.RETURN_FROM_BANK and self._bank.status != PaymentStatus.REDIRECT_TO_BANK:
            logging.debug("Payment status is not status suitable.", extra={'status': self._bank.status})
            raise BankGatewayStateInvalid(
                "You change the status bank record before/after this record change status from redirect to bank. "
                "current status is {}".format(
                    self._bank.status
                )
            )
        self._bank.status = payment_status
        self._bank.save()
        logging.debug("Change bank payment status", extra={'status': payment_status})

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
