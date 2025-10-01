from decimal import Decimal
from typing import Protocol

from azbankgateways.v3.exceptions.internal import BankGatewayMinimumAmountError
from azbankgateways.v3.interfaces import MessageServiceInterface, OrderDetails


class _HasMinimumAmountAndMessageService(Protocol):
    @property
    def minimum_amount(self) -> Decimal:
        ...

    @property
    def message_service(self) -> MessageServiceInterface:
        ...


class MinimumAmountCheckMixin:
    """Provides reusable minimum amount check for payment providers."""

    def check_minimum_amount(self: _HasMinimumAmountAndMessageService, order_details: OrderDetails) -> None:
        if order_details.amount < self.minimum_amount:
            raise BankGatewayMinimumAmountError(order_details, self.minimum_amount)
