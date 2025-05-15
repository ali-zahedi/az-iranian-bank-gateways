from __future__ import annotations

from django.urls import path

from . import default_settings as settings
from .apps import AZIranianBankGatewaysConfig
from .views import callback_view
from .views import go_to_bank_gateway
from .views import sample_payment_view
from .views import sample_result_view

app_name = AZIranianBankGatewaysConfig.name

_urlpatterns = [
    path("callback/", callback_view, name="callback"),
]

if not settings.IS_SAFE_GET_GATEWAY_PAYMENT:
    _urlpatterns += [
        path("go-to-bank-gateway/", go_to_bank_gateway, name="go-to-bank-gateway"),
    ]

if settings.IS_SAMPLE_FORM_ENABLE:
    _urlpatterns += [
        path("sample-payment/", sample_payment_view, name="sample-payment"),
        path("sample-result/", sample_result_view, name="sample-result"),
    ]


def az_bank_gateways_urls():
    return _urlpatterns, app_name, app_name
