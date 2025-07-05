"""
Default configuration and utility functions for managing Iranian bank gateways
using azbankgateways integration in a Django environment.
"""

import importlib
from django.conf import settings
from azbankgateways.apps import AZIranianBankGatewaysConfig

# Load settings from Django configuration
_BANK_GATEWAY_SETTINGS = getattr(settings, "AZ_IRANIAN_BANK_GATEWAYS", {})

# Define bank classes with fallbacks
BANK_CLASS = getattr(settings, "CLASS", {
    "BMI": "azbankgateways.banks.BMI",
    "SEP": "azbankgateways.banks.SEP",
    "ZARINPAL": "azbankgateways.banks.Zarinpal",
    "IDPAY": "azbankgateways.banks.IDPay",
    "ZIBAL": "azbankgateways.banks.Zibal",
    "BAHAMTA": "azbankgateways.banks.Bahamta",
    "MELLAT": "azbankgateways.banks.Mellat",
    "PAYV1": "azbankgateways.banks.PayV1",
})

# Gateway configuration values
BANK_PRIORITIES = _BANK_GATEWAY_SETTINGS.get("BANK_PRIORITIES", [])
BANK_GATEWAYS = _BANK_GATEWAY_SETTINGS.get("GATEWAYS", {})
BANK_DEFAULT = _BANK_GATEWAY_SETTINGS.get("DEFAULT", "BMI")
SETTING_VALUE_READER_CLASS = _BANK_GATEWAY_SETTINGS.get(
    "SETTING_VALUE_READER_CLASS", "azbankgateways.readers.DefaultReader"
)
CURRENCY = _BANK_GATEWAY_SETTINGS.get("CURRENCY", "IRR")
TRACKING_CODE_QUERY_PARAM = _BANK_GATEWAY_SETTINGS.get("TRACKING_CODE_QUERY_PARAM", "tc")
TRACKING_CODE_LENGTH = _BANK_GATEWAY_SETTINGS.get("TRACKING_CODE_LENGTH", 16)
IS_SAMPLE_FORM_ENABLE = _BANK_GATEWAY_SETTINGS.get("IS_SAMPLE_FORM_ENABLE", False)
IS_SAFE_GET_GATEWAY_PAYMENT = _BANK_GATEWAY_SETTINGS.get("IS_SAFE_GET_GATEWAY_PAYMENT", False)
CUSTOM_APP = _BANK_GATEWAY_SETTINGS.get("CUSTOM_APP")

# Define namespaced URLs
APP_NAMESPACE = f"{CUSTOM_APP}:{AZIranianBankGatewaysConfig.name}" if CUSTOM_APP else AZIranianBankGatewaysConfig.name
CALLBACK_NAMESPACE = _BANK_GATEWAY_SETTINGS.get("CALLBACK_NAMESPACE", f"{APP_NAMESPACE}:callback")
GO_TO_BANK_GATEWAY_NAMESPACE = _BANK_GATEWAY_SETTINGS.get("GO_TO_BANK_GATEWAY_NAMESPACE", f"{APP_NAMESPACE}:go-to-bank-gateway")
SAMPLE_RESULT_NAMESPACE = _BANK_GATEWAY_SETTINGS.get("SAMPLE_RESULT_NAMESPACE", f"{APP_NAMESPACE}:sample-result")


# Utility Functions

def get_bank_class(bank_name):
    """Dynamically import and return the class for the given bank name."""
    class_path = BANK_CLASS.get(bank_name)
    if not class_path:
        raise ValueError(f"No bank class defined for '{bank_name}'")
    module_path, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def get_default_bank_class():
    """Get the class for the default bank gateway."""
    return get_bank_class(BANK_DEFAULT)


def is_gateway_enabled(bank_name):
    """Return True if a bank gateway is enabled, False otherwise."""
    return BANK_GATEWAYS.get(bank_name, {}).get("ENABLED", False)


def get_enabled_gateways():
    """Return a list of all enabled gateways."""
    return [bank for bank in BANK_GATEWAYS if is_gateway_enabled(bank)]


def get_tracking_code_length():
    """Return the tracking code length configured."""
    return TRACKING_CODE_LENGTH


def get_currency():
    """Return the default currency configured."""
    return CURRENCY


def get_callback_url(namespace=None):
    """Return the callback URL namespace."""
    return namespace or CALLBACK_NAMESPACE


def get_go_to_gateway_url(namespace=None):
    """Return the go-to gateway URL namespace."""
    return namespace or GO_TO_BANK_GATEWAY_NAMESPACE


def get_sample_result_url(namespace=None):
    """Return the sample result URL namespace."""
    return namespace or SAMPLE_RESULT_NAMESPACE


def get_reader_class():
    """Dynamically import and return the configured value reader class."""
    module_path, class_name = SETTING_VALUE_READER_CLASS.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def get_bank_priority_list():
    """Return the list of configured bank priorities."""
    return BANK_PRIORITIES


def get_custom_app():
    """Return the name of the custom app if provided."""
    return CUSTOM_APP


def is_sample_form_enabled():
    """Return True if sample form is enabled."""
    return IS_SAMPLE_FORM_ENABLE


def is_safe_get_gateway_payment():
    """Return True if GET-safe gateway payment is enabled."""
    return IS_SAFE_GET_GATEWAY_PAYMENT
 
