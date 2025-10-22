from __future__ import annotations

from decimal import Decimal
from typing import Protocol


class ProviderProtocol(Protocol):
    @property
    def minimum_amount(self) -> Decimal:
        ...
