class AZBankGatewaysException(Exception):
    """AZ bank gateways exception"""


class BankGatewayConnectionError(AZBankGatewaysException):
    """The requested gateway connection error"""


class BankGatewayRejectPayment(AZBankGatewaysException):
    """The requested bank reject payment"""


class BankGatewayHttpResponseError(AZBankGatewaysException):
    """Base class for all HttpResponse related errors."""
