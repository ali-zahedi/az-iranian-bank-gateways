from django.shortcuts import redirect

from azbankgateways.exceptions import BankGatewayUnclear
from azbankgateways.bankfactories import BankFactory


def callback_view(request):
    bank_type = request.GET.get('bank_type', None)
    if not bank_type:
        raise BankGatewayUnclear()

    factory = BankFactory(bank_type)
    bank = factory.create()
    bank.verify_from_gateway(request)
    return redirect('https://www.zarinpal.com/pg/StartPay/%s/ZarinGate' % (str(result.Authority)))
