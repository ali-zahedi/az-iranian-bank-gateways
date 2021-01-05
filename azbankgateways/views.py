import logging
from urllib.parse import unquote

from django.shortcuts import render

from azbankgateways.bankfactories import BankFactory
from azbankgateways.exceptions import BankGatewayUnclear


def callback_view(request):
    bank_type = request.GET.get('bank_type', None)
    identifier = request.GET.get('identifier', None)
    if not bank_type:
        logging.critical("Bank type is required. but it doesnt send.")
        raise BankGatewayUnclear("Bank type is required")

    factory = BankFactory()
    bank = factory.create(bank_type, identifier=identifier)
    bank.verify_from_gateway(request)
    return bank.redirect_client_callback()


def go_to_bank_gateway(request):
    context = {
        'params': {}
    }
    for key, value in request.GET.items():
        if key == 'url' or key == 'method':
            context[key] = unquote(value)
        else:
            context['params'][key] = unquote(value)

    return render(
        request,
        'azbankgateways/redirect_to_bank.html',
        context=context
    )
