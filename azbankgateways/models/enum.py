from django.utils.translation import gettext_lazy as _

import azbankgateways.default_settings as settings


class BankType(settings.TEXT_CHOICES):
    BMI = 'BMI', _('BMI')
    SEP = 'SEP', _('SEP')
    ZARINPAL = 'ZARINPAL', _('Zarinpal')
    IDPAY = 'IDPAY', _('IDPay')
    ZIBAL = 'ZIBAL', _('Zibal')
    BAHAMTA = 'BAHAMTA', _('Bahamta')


class CurrencyEnum(settings.TEXT_CHOICES):
    IRR = 'IRR', _('Rial')
    IRT = 'IRT', _('Toman')

    @classmethod
    def rial_to_toman(cls, amount):
        return amount / 10

    @classmethod
    def toman_to_rial(cls, amount):
        return amount * 10


class PaymentStatus(settings.TEXT_CHOICES):
    WAITING = _('Waiting')
    REDIRECT_TO_BANK = _('Redirect to bank')
    RETURN_FROM_BANK = _('Return from bank')
    CANCEL_BY_USER = _('Cancel by user')
    EXPIRE_GATEWAY_TOKEN = _('Expire gateway token')
    EXPIRE_VERIFY_PAYMENT = _('Expire verify payment')
    COMPLETE = _('Complete')
