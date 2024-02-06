class azbankException(Exception):
    """AZ bank gateways exception"""


class SettingDoesNotExist(azbankException):
    """The requested setting does not exist"""


class CurrencyDoesNotSupport(azbankException):
    """The requested currency does not support"""


class AmountDoesNotSupport(azbankException):
    """The requested amount does not support"""


class BankGatewayConnectionError(azbankException):
    """The requested gateway connection error"""


class BankGatewayRejectPayment(azbankException):
    """The requested bank reject payment"""


class BankGatewayTokenExpired(azbankException):
    """The requested bank token expire"""


class BankGatewayUnclear(azbankException):
    """The requested bank unclear"""


class BankGatewayStateInvalid(azbankException):
    """The requested bank unclear"""


class BankGatewayAutoConnectionFailed(azbankException):
    """The auto connection cant find bank"""


class SafeSettingsEnabled(azbankException):
    """This feature is disabled when the safe gateway is active"""
