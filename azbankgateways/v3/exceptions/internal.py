from azbankgateways.v3.exceptions import AZBankGatewaysException
from azbankgateways.v3.interfaces import (
    HttpRequestInterface,
    HttpResponseInterface,
    OrderDetails,
)


class AzBankInternalExceptions(AZBankGatewaysException):
    pass


class BankGatewayMinimumAmountError(AzBankInternalExceptions):
    def __init__(self, order_details: OrderDetails, minimum_amount, *args) -> None:
        self.order_details = order_details
        self.minimum_amount = minimum_amount
        super().__init__(
            f"Amount {self.order_details.amount} is below the minimum required {self.minimum_amount}.", *args
        )


class BankGatewayRejectPayment(AzBankInternalExceptions):
    """The requested bank reject payment"""

    def __init__(self, message: str, *args) -> None:
        self.message = message
        super().__init__(f"Bank rejected payment: {self.message}", *args)


class BankGatewayConnectionError(AzBankInternalExceptions):
    """The requested gateway connection error"""

    def __init__(self, request: HttpRequestInterface, exception: Exception, *args) -> None:
        self.request = request
        self.exception = exception
        super().__init__(*args)


class BankGatewayInvalidJsonError(AzBankInternalExceptions):
    """Raised when the response is not valid JSON (wrong content-type or decode error)."""

    def __init__(self, response: HttpResponseInterface, message: str, *args) -> None:
        self.response = response
        self.message = message
        super().__init__(response, f"Invalid JSON response: {self.message}", *args)
