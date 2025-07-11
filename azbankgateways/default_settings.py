"""
Cleaned-up and enhanced default configuration for Azbankgateways.
"""

from django.conf import settings
from azbankgateways.apps import AZIranianBankGatewaysConfig
from urllib.parse import urlencode
import importlib

# Default bank class mapping fallback
DEFAULT_BANK_CLASSES = {
    "BMI": "azbankgateways.banks.BMI",
    "SEP": "azbankgateways.banks.SEP",
    "ZARINPAL": "azbankgateways.banks.Zarinpal",
    "IDPAY": "azbankgateways.banks.IDPay",
    "ZIBAL": "azbankgateways.banks.Zibal",
    "BAHAMTA": "azbankgateways.banks.Bahamta",
    "MELLAT": "azbankgateways.banks.Mellat",
    "PAYV1": "azbankgateways.banks.PayV1",
}

# Load configurations
BANK_CLASS = getattr(settings, "CLASS", DEFAULT_BANK_CLASSES)
AZ_GATEWAY_CONF = getattr(settings, "AZ_IRANIAN_BANK_GATEWAYS", {})

BANK_PRIORITIES = AZ_GATEWAY_CONF.get("BANK_PRIORITIES", [])
BANK_GATEWAYS = AZ_GATEWAY_CONF.get("GATEWAYS", {})
BANK_DEFAULT = AZ_GATEWAY_CONF.get("DEFAULT", "BMI")
SETTING_VALUE_READER_CLASS = AZ_GATEWAY_CONF.get("SETTING_VALUE_READER_CLASS", "azbankgateways.readers.DefaultReader")
CURRENCY = AZ_GATEWAY_CONF.get("CURRENCY", "IRR")
TRACKING_CODE_QUERY_PARAM = AZ_GATEWAY_CONF.get("TRACKING_CODE_QUERY_PARAM", "tc")
TRACKING_CODE_LENGTH = AZ_GATEWAY_CONF.get("TRACKING_CODE_LENGTH", 16)
IS_SAMPLE_FORM_ENABLE = AZ_GATEWAY_CONF.get("IS_SAMPLE_FORM_ENABLE", False)
IS_SAFE_GET_GATEWAY_PAYMENT = AZ_GATEWAY_CONF.get("IS_SAFE_GET_GATEWAY_PAYMENT", False)
CUSTOM_APP = AZ_GATEWAY_CONF.get("CUSTOM_APP")

# Namespaces for views
namespace_prefix = f"{CUSTOM_APP}:" if CUSTOM_APP else ""
CALLBACK_NAMESPACE = AZ_GATEWAY_CONF.get("CALLBACK_NAMESPACE", f"{namespace_prefix}{AZIranianBankGatewaysConfig.name}:callback")
GO_TO_BANK_GATEWAY_NAMESPACE = AZ_GATEWAY_CONF.get("GO_TO_BANK_GATEWAY_NAMESPACE", f"{namespace_prefix}{AZIranianBankGatewaysConfig.name}:go-to-bank-gateway")
SAMPLE_RESULT_NAMESPACE = AZ_GATEWAY_CONF.get("SAMPLE_RESULT_NAMESPACE", f"{namespace_prefix}{AZIranianBankGatewaysConfig.name}:sample-result")


def get_bank_class(bank_name):
    class_path = BANK_CLASS.get(bank_name)
    if not class_path:
        raise ValueError(f"Undefined bank class for: {bank_name}")
    module_name, class_name = class_path.rsplit(".", 1)
    return getattr(importlib.import_module(module_name), class_name)


def get_priority_banks():
    return BANK_PRIORITIES or list(BANK_CLASS.keys())


def is_gateway_supported(gateway_name):
    return gateway_name in BANK_GATEWAYS


def get_setting(key, default=None):
    return AZ_GATEWAY_CONF.get(key, default)


def get_callback_url(transaction_id):
    return f"/{CALLBACK_NAMESPACE}?{TRACKING_CODE_QUERY_PARAM}={transaction_id}"


def get_all_gateways():
    return BANK_GATEWAYS


def get_default_gateway():
    return BANK_DEFAULT


def build_gateway_redirect_url(gateway_name, transaction_id):
    if not is_gateway_supported(gateway_name):
        raise ValueError(f"Unsupported gateway: {gateway_name}")
    query = urlencode({TRACKING_CODE_QUERY_PARAM: transaction_id})
    return f"/{GO_TO_BANK_GATEWAY_NAMESPACE}/{gateway_name}/?{query}"


def get_currency():
    return CURRENCY


def is_sample_form_enabled():
    return IS_SAMPLE_FORM_ENABLE


def is_safe_get_enabled():
    return IS_SAFE_GET_GATEWAY_PAYMENT


def get_all_supported_bank_names():
    return list(BANK_CLASS.keys())


def get_gateway_details(gateway_name):
    return BANK_GATEWAYS.get(gateway_name, {})


def has_custom_app_namespace():
    return bool(CUSTOM_APP)


def get_tracking_code_length():
    return TRACKING_CODE_LENGTH


def get_tracking_code_param():
    return TRACKING_CODE_QUERY_PARAM
 
