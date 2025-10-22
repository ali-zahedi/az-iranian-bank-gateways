from typing import Self

from azbankgateways.v3.exceptions.internal import InternalMinimumAmountError
from azbankgateways.v3.interfaces import OrderDetails
from azbankgateways.v3.protocols import ProviderProtocol


class MinimumAmountCheckMixin:
    """Provides reusable minimum amount check for payment providers."""

    def check_minimum_amount(self: ProviderProtocol, order_details: OrderDetails) -> None:
        if order_details.amount < self.minimum_amount:
            raise InternalMinimumAmountError(order_details, self.minimum_amount)


class NoDirectInitMixin:
    def __init__(self, *args, **kwargs):
        if not getattr(self, "allow_init", False):
            raise RuntimeError(
                f"Direct instantiation of {self.__class__.__name__} is not allowed. "
                f"Use {self.__class__.__name__}.create(...)"
            )
        super().__init__(*args, **kwargs)  # Call next __init__ in MRO

    @classmethod
    def create(cls, *args, **kwargs) -> Self:
        obj = cls.__new__(cls)
        obj.allow_init = True
        obj.__init__(*args, **kwargs)
        obj.allow_init = False
        return obj
