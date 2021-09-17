import logging
from urllib.parse import unquote

from django.http import Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from azbankgateways.bankfactories import BankFactory
from azbankgateways.exceptions import AZBankGatewaysException


@csrf_exempt
def callback_view(request):
    bank_type = request.GET.get('bank_type', None)
    identifier = request.GET.get('identifier', None)

    if not bank_type:
        logging.critical("Bank type is required. but it doesnt send.")
        raise Http404

    factory = BankFactory()
    bank = factory.create(bank_type, identifier=identifier)
    try:
        bank.verify_from_gateway(request)
    except AZBankGatewaysException:
        logging.exception("Verify from gateway failed.", stack_info=True)
    return bank.redirect_client_callback()


@csrf_exempt
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
