from azbankgateways.v3.interfaces import (
    BankEntityInterface,
    HTTPRequestInterface,
    OrderDetails,
    ProviderInterface,
)


class PaymentGateway:
    # ???
    def __init__(self, provider: ProviderInterface, storage: BankEntityInterface):
        self.provider = provider
        self.storage = storage

    def create_payment_request(self, order_details: OrderDetails) -> HTTPRequestInterface:
        return self.provider.create_payment_request(order_details)

    # def process_payment(self, transaction_data):
    # self.provider.process_transaction(transaction_data)
    # self.storage.save(transaction_data)
    # raise NotImplementedError()
