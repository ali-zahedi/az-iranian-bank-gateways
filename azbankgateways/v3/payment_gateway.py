from .interfaces import BankEntityInterface, ProviderInterface, RedirectRequestInterface


class PaymentGateway:
    # ???
    def __init__(self, provider: ProviderInterface, storage: BankEntityInterface):
        self.provider = provider
        self.storage = storage

    def request_pay(self) -> RedirectRequestInterface:
        return self.provider.get_request_pay()

    def process_payment(self, transaction_data):
        # self.provider.process_transaction(transaction_data)
        # self.storage.save(transaction_data)
        raise NotImplementedError()
