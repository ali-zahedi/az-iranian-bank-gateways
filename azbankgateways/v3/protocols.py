from __future__ import annotations

from decimal import Decimal
from typing import Protocol


class MinimumAmountCheckMixinProtocol(Protocol):
    @property
    def minimum_amount(self) -> Decimal:
        ...
