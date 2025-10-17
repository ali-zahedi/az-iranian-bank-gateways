from azbankgateways.v3.exceptions.internal import InternalMinimumAmountError
from azbankgateways.v3.interfaces import OrderDetails
from azbankgateways.v3.protocols import MinimumAmountCheckMixinProtocol


class MinimumAmountCheckMixin:
    """Provides reusable minimum amount check for payment providers."""

    def check_minimum_amount(self: MinimumAmountCheckMixinProtocol, order_details: OrderDetails) -> None:
        if order_details.amount < self.minimum_amount:
            raise InternalMinimumAmountError(order_details, self.minimum_amount)
