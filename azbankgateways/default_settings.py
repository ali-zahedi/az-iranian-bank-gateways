"""Default settings for messaging."""

from django.conf import settings
from azbankgateways.apps import AZIranianBankGatewaysConfig

_AZ_IRANIAN_BANK_GATEWAYS = getattr(settings, 'AZ_IRANIAN_BANK_GATEWAYS', {})
BANK_GATEWAYS = _AZ_IRANIAN_BANK_GATEWAYS.get('GATEWAYS', {})
BANK_DEFAULT = _AZ_IRANIAN_BANK_GATEWAYS.get('DEFAULT', 'BMI')
CURRENCY = _AZ_IRANIAN_BANK_GATEWAYS.get('CURRENCY', 'IRR')
TRACKING_CODE_QUERY_PARAM = _AZ_IRANIAN_BANK_GATEWAYS.get('TRACKING_CODE_QUERY_PARAM', 'tc')
TRACKING_CODE_LENGTH = _AZ_IRANIAN_BANK_GATEWAYS.get('TRACKING_CODE_LENGTH', 16)
CALLBACK_NAMESPACE = f'{AZIranianBankGatewaysConfig.name}:callback'
GO_TO_BANK_GATEWAY_NAMESPACE = f'{AZIranianBankGatewaysConfig.name}:go-to-bank-gateway'
