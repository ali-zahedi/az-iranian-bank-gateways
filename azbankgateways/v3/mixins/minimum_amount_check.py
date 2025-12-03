from azbankgateways.v3.exceptions.internal import InternalMinimumAmountError
from azbankgateways.v3.interfaces import OrderDetails
from azbankgateways.v3.protocols import ProviderProtocol


class MinimumAmountCheckMixin:
    """Provides reusable minimum amount check for payment providers."""

    def check_minimum_amount(self: ProviderProtocol, order_details: OrderDetails) -> None:
        if order_details.amount < self.minimum_amount:
            raise InternalMinimumAmountError(order_details, self.minimum_amount)
