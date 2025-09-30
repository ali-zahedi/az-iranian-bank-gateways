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


class SafeSettingsEnabled(AZBankGatewaysException):
    """This feature is disabled when the safe gateway is active"""


class HttpResponseError(AZBankGatewaysException):
    """Base class for all HttpResponse related errors."""


class ResponseIsNotJSONError(HttpResponseError):
    """Raised when .json() is called but Content-Type is not application/json."""


class JSONDecodeError(HttpResponseError):
    """Raised when response body cannot be decoded as JSON."""
