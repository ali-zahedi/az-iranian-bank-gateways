from django.urls import path
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from datetime import datetime

from . import default_settings as settings
from .apps import AZIranianBankGatewaysConfig
from .views import (
    callback_view,
    go_to_bank_gateway,
    sample_payment_view,
    sample_result_view,
)

app_name = AZIranianBankGatewaysConfig.name

urlpatterns = [
    path("callback/", callback_view, name="callback"),
]

if not settings.IS_SAFE_GET_GATEWAY_PAYMENT:
    urlpatterns.append(
        path("go-to-bank-gateway/", go_to_bank_gateway, name="go-to-bank-gateway")
    )

if settings.IS_SAMPLE_FORM_ENABLE:
    urlpatterns += [
        path("sample-payment/", sample_payment_view, name="sample-payment"),
        path("sample-result/", sample_result_view, name="sample-result"),
    ]

# Gateway status view
urlpatterns.append(
    path("gateway-status/", lambda request: JsonResponse({
        "gateway_enabled": not settings.IS_SAFE_GET_GATEWAY_PAYMENT,
        "sample_form_enabled": settings.IS_SAMPLE_FORM_ENABLE,
    }), name="gateway-status")
)

# Diagnostic check view
urlpatterns.append(
    path("diagnostic-check/", lambda request: JsonResponse({
        "message": "Bank Gateway Module is active.",
        "app": app_name,
    }), name="diagnostic-check")
)

# Settings info view
urlpatterns.append(
    path("gateway-settings/", lambda request: JsonResponse({
        "IS_SAFE_GET_GATEWAY_PAYMENT": settings.IS_SAFE_GET_GATEWAY_PAYMENT,
        "IS_SAMPLE_FORM_ENABLE": settings.IS_SAMPLE_FORM_ENABLE,
    }), name="gateway-settings")
)

# Method test view
urlpatterns.append(
    path("method-test/", lambda request: JsonResponse({
        "message": "POST method accepted."
    }) if request.method == "POST" else HttpResponseNotAllowed(["POST"]), name="method-test")
)

# Server time view
urlpatterns.append(
    path("server-time/", lambda request: JsonResponse({
        "server_time": datetime.now().isoformat()
    }), name="server-time")
)

# Echo view for debug
urlpatterns.append(
    path("echo/", lambda request: JsonResponse({"received": request.POST.dict()})
         if request.method == "POST" else HttpResponseNotAllowed(["POST"]), name="echo")
)

# Module info view
urlpatterns.append(
    path("module-info/", lambda request: JsonResponse({
        "module": "AZ Iranian Bank Gateways",
        "version": "1.0.0",
        "author": "Phoenix Marie",
        "features": [
            "payment callback",
            "gateway redirection",
            "sample form handling",
            "diagnostics",
            "settings exposure",
            "debugging tools",
        ]
    }), name="module-info")
)

def az_bank_gateways_urls():
    return urlpatterns, app_name, app_name
 
