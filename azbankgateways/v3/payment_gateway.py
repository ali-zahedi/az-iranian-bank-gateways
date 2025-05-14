from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from .interfaces import BankEntityInterface
    from .interfaces import ProviderInterface
    from .interfaces import RequestInterface


class PaymentGateway:
    # ???
    def __init__(self, provider: ProviderInterface, storage: BankEntityInterface):
        self.provider = provider
        self.storage = storage

    def request_pay(self) -> RequestInterface:
        return self.provider.get_request_pay()

    def process_payment(self, transaction_data: Any) -> None:
        # self.provider.process_transaction(transaction_data)
        # self.storage.save(transaction_data)
        raise NotImplementedError()
