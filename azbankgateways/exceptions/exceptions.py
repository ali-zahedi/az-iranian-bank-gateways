class AZBankGatewaysException(Exception):
    """AZ bank gateways exception"""

class SettingDoesNotExist(AZBankGatewaysException):
    """The requested setting does not exist"""

class CurrencyDoesNotSupport(AZBankGatewaysException):
    """The requested currency does not support"""

class AmountDoesNotSupport(AZBankGatewaysException):
    """The requested amount does not support"""

class BankGatewayConnectionError(AZBankGatewaysException):
    """The requested gateway connection error"""

class BankGatewayRejectPayment(AZBankGatewaysException):
    """The requested bank reject payment"""

class BankGatewayTokenExpired(AZBankGatewaysException):
    """The requested bank token expire"""

class BankGatewayUnclear(AZBankGatewaysException):
    """The requested bank unclear"""

class BankGatewayStateInvalid(AZBankGatewaysException):
    """The requested bank unclear"""

class BankGatewayAutoConnectionFailed(AZBankGatewaysException):
    """The auto connection cant find bank"""
