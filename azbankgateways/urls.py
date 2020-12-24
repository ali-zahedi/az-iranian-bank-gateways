from django.urls import path
from .apps import AZIranianBankGatewaysConfig
from .views import callback_view, go_to_bank_gateway

app_name = AZIranianBankGatewaysConfig.name

_urlpatterns = [
    path('callback/', callback_view, name='callback'),
    path('go-to-bank-gateway/', go_to_bank_gateway, name='go-to-bank-gateway'),
]


def az_bank_gateways_urls():
    return _urlpatterns, app_name, app_name
