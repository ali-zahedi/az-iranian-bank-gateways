from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Protocol


if TYPE_CHECKING:
    from azbankgateways.v3.interfaces import (
        HTTPRequestInterface,
        OrderDetails,
        ProviderName,
    )


class ProviderProtocol(Protocol):
    @property
    def minimum_amount(self) -> Decimal:
        ...

    @property
    def name(self) -> ProviderName:
        ...

    def create_payment_request(self, order_details: OrderDetails) -> HTTPRequestInterface:
        ...

    def verify_payment(self, reference_number: str, amount: Decimal) -> bool:
        ...

    def check_minimum_amount(self, order_details: OrderDetails) -> None:
        ...
