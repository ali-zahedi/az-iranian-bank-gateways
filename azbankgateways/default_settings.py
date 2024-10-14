"""Default settings for messaging."""

from django.conf import settings

from azbankgateways.apps import AZIranianBankGatewaysConfig


BANK_CLASS = getattr(
    settings,
    "CLASS",
    {
        "BMI": "azbankgateways.banks.BMI",
        "SEP": "azbankgateways.banks.SEP",
        "ZARINPAL": "azbankgateways.banks.Zarinpal",
        "IDPAY": "azbankgateways.banks.IDPay",
        "ZIBAL": "azbankgateways.banks.Zibal",
        "BAHAMTA": "azbankgateways.banks.Bahamta",
        "MELLAT": "azbankgateways.banks.Mellat",
        "PAYV1": "azbankgateways.banks.PayV1",
    },
)
_AZ_IRANIAN_BANK_GATEWAYS = getattr(settings, "AZ_IRANIAN_BANK_GATEWAYS", {})
BANK_PRIORITIES = _AZ_IRANIAN_BANK_GATEWAYS.get("BANK_PRIORITIES", [])
BANK_GATEWAYS = _AZ_IRANIAN_BANK_GATEWAYS.get("GATEWAYS", {})
BANK_DEFAULT = _AZ_IRANIAN_BANK_GATEWAYS.get("DEFAULT", "BMI")
SETTING_VALUE_READER_CLASS = _AZ_IRANIAN_BANK_GATEWAYS.get(
    "SETTING_VALUE_READER_CLASS", "azbankgateways.readers.DefaultReader"
)
CURRENCY = _AZ_IRANIAN_BANK_GATEWAYS.get("CURRENCY", "IRR")
TRACKING_CODE_QUERY_PARAM = _AZ_IRANIAN_BANK_GATEWAYS.get("TRACKING_CODE_QUERY_PARAM", "tc")
TRACKING_CODE_LENGTH = _AZ_IRANIAN_BANK_GATEWAYS.get("TRACKING_CODE_LENGTH", 16)
IS_SAMPLE_FORM_ENABLE = _AZ_IRANIAN_BANK_GATEWAYS.get("IS_SAMPLE_FORM_ENABLE", False)
IS_SAFE_GET_GATEWAY_PAYMENT = _AZ_IRANIAN_BANK_GATEWAYS.get("IS_SAFE_GET_GATEWAY_PAYMENT", False)
CUSTOM_APP = _AZ_IRANIAN_BANK_GATEWAYS.get("CUSTOM_APP")
if CUSTOM_APP:
    CALLBACK_NAMESPACE = f"{CUSTOM_APP}:{AZIranianBankGatewaysConfig.name}:callback"
    GO_TO_BANK_GATEWAY_NAMESPACE = f"{CUSTOM_APP}:{AZIranianBankGatewaysConfig.name}:go-to-bank-gateway"
    SAMPLE_RESULT_NAMESPACE = f"{CUSTOM_APP}:{AZIranianBankGatewaysConfig.name}:sample-result"
else:
    CALLBACK_NAMESPACE = _AZ_IRANIAN_BANK_GATEWAYS.get(
        "CALLBACK_NAMESPACE", f"{AZIranianBankGatewaysConfig.name}:callback"
    )
    GO_TO_BANK_GATEWAY_NAMESPACE = _AZ_IRANIAN_BANK_GATEWAYS.get(
        "GO_TO_BANK_GATEWAY_NAMESPACE", f"{AZIranianBankGatewaysConfig.name}:go-to-bank-gateway"
    )
    SAMPLE_RESULT_NAMESPACE = _AZ_IRANIAN_BANK_GATEWAYS.get(
        "SAMPLE_RESULT_NAMESPACE", f"{AZIranianBankGatewaysConfig.name}:sample-result"
    )
