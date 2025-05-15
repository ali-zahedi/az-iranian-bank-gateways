from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .interfaces import Currency


class CurrencyRegistry:
    __currencies: dict[str, Currency] = {}

    @classmethod
    def register_currency(cls, currency: Currency) -> None:
        cls.__currencies[currency.value] = currency

    @classmethod
    def get_currency(cls, code: str) -> Currency:
        return cls.__currencies[code]

    @classmethod
    def list_currencies(cls) -> list[Currency]:
        return list(cls.__currencies.values())
