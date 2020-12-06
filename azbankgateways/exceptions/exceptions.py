class SettingDoesNotExist(Exception):
    """The requested setting does not exist"""

class CurrencyDoesNotSupport(Exception):
    """The requested currency does not support"""

class AmountDoesNotSupport(Exception):
    """The requested amount does not support"""

class BankGatewayConnectionError(Exception):
    """The requested gateway connection error"""

class BankGatewayRejectPayment(Exception):
    """The requested bank reject payment"""

class BankGatewayTokenExpired(Exception):
    """The requested bank token expire"""

class BankGatewayUnclear(Exception):
    """The requested bank unclear"""

class BankGatewayStateInvalid(Exception):
    """The requested bank unclear"""
