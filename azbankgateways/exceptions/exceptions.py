class SettingDoesNotExist(Exception):
    """The requested setting does not exist"""

class CurrencyDoesNotSupport(Exception):
    """The requested currency does not support"""

class AmountDoesNotSupport(Exception):
    """The requested amount does not support"""
