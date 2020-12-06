from azbankgateways.bankfactories import BankFactory
from azbankgateways.exceptions import BankGatewayUnclear


def callback_view(request):
    bank_type = request.GET.get('bank_type', None)
    if not bank_type:
        raise BankGatewayUnclear()

    factory = BankFactory(bank_type)
    bank = factory.create()
    bank.verify_from_gateway(request)
    return bank.redirect_callback()
