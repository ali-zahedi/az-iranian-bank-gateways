"""Default settings for messaging."""

from django.conf import settings
from azbankgateways.apps import AZIranianBankGatewaysConfig
import django

if django.__version__ >= '3.0':
    from django.db import models

    TEXT_CHOICES = models.TextChoices
else:
    from .models.enum_django import TextChoices

    TEXT_CHOICES = TextChoices
BANK_CLASS = getattr(
    settings,
    'CLASS',
    {
        'BMI': 'azbankgateways.banks.BMI',
        'SEP': 'azbankgateways.banks.SEP',
        'ZARINPAL': 'azbankgateways.banks.Zarinpal',
        'IDPAY': 'azbankgateways.banks.IDPay',
        'ZIBAL': 'azbankgateways.banks.Zibal',
        'BAHAMTA': 'azbankgateways.banks.Bahamta',
    }
)
_AZ_IRANIAN_BANK_GATEWAYS = getattr(settings, 'AZ_IRANIAN_BANK_GATEWAYS', {})
BANK_PRIORITIES = _AZ_IRANIAN_BANK_GATEWAYS.get('BANK_PRIORITIES', [])
BANK_GATEWAYS = _AZ_IRANIAN_BANK_GATEWAYS.get('GATEWAYS', {})
BANK_DEFAULT = _AZ_IRANIAN_BANK_GATEWAYS.get('DEFAULT', 'BMI')
SETTING_VALUE_READER_CLASS = _AZ_IRANIAN_BANK_GATEWAYS.get('SETTING_VALUE_READER_CLASS', 'azbankgateways.readers.DefaultReader')
CURRENCY = _AZ_IRANIAN_BANK_GATEWAYS.get('CURRENCY', 'IRR')
TRACKING_CODE_QUERY_PARAM = _AZ_IRANIAN_BANK_GATEWAYS.get('TRACKING_CODE_QUERY_PARAM', 'tc')
TRACKING_CODE_LENGTH = _AZ_IRANIAN_BANK_GATEWAYS.get('TRACKING_CODE_LENGTH', 16)
CALLBACK_NAMESPACE = f'{AZIranianBankGatewaysConfig.name}:callback'
GO_TO_BANK_GATEWAY_NAMESPACE = f'{AZIranianBankGatewaysConfig.name}:go-to-bank-gateway'
