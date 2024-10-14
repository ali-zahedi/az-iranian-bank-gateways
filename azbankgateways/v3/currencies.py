from typing import Dict

from .interfaces import Currency


class CurrencyRegistry:
    __currencies: Dict[str, Currency] = {}

    @classmethod
    def register_currency(cls, currency: Currency):
        cls.__currencies[currency.value] = currency

    @classmethod
    def get_currency(cls, code: str) -> Currency:
        return cls.__currencies.get(code)

    @classmethod
    def list_currencies(cls):
        return list(cls.__currencies.values())
