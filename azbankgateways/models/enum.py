from django.db import models
from django.utils.translation import gettext_lazy as _


class BankType(models.TextChoices):
    BMI = 'BMI', _('BMI')
    ZARINPAL = 'ZARINPAL', _('Zarinpal')


class CurrencyEnum(models.TextChoices):
    IRR = 'IRR', _('Rial')
    IRT = 'IRT', _('Toman')

    @classmethod
    def rial_to_toman(cls, amount):
        return amount / 10

    @classmethod
    def toman_to_rial(cls, amount):
        return amount * 10
