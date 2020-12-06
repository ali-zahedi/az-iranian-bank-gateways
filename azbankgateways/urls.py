from django.urls import path
from .apps import AZIranianBankGatewaysConfig
from .views import callback_view

app_name = AZIranianBankGatewaysConfig.name

_urlpatterns = [
    path('callback/', callback_view, name='callback'),
]


def az_bank_gateways_urls():
    return _urlpatterns, app_name, app_name
