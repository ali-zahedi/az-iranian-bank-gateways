from __future__ import annotations

import decimal

from azbankgateways.v3.interfaces import (
    HttpRequestInterface,
    HttpResponseInterface,
    OrderDetails,
)


class AZBankInternalException(Exception):
    default_message = "An Internal error occurred in AZBank gateway."

    def __init__(self, message: str | None = None, *args):
        self.message = message or self.default_message
        super().__init__(self.message, *args)


class InternalMinimumAmountError(AZBankInternalException):
    default_message = "The order amount is below the minimum allowed."

    def __init__(
        self, order_details: OrderDetails, minimum_amount: decimal.Decimal, message: str | None = None, *args
    ) -> None:
        self.order_details = order_details
        self.minimum_amount = minimum_amount
        super().__init__(message, *args)


class InternalRejectPaymentError(AZBankInternalException):
    default_message = "Bank rejected the payment."

    def __init__(self, bank_message: str, message: str | None = None, *args) -> None:
        self.bank_message = bank_message
        super().__init__(message, *args)


class InternalConnectionError(AZBankInternalException):
    default_message = "Failed to connect to the bank gateway."

    def __init__(
        self, request: HttpRequestInterface, exception: Exception, message: str | None = None, *args
    ) -> None:
        self.request = request
        self.exception = exception
        super().__init__(message, *args)


class InternalInvalidJsonError(AZBankInternalException):
    default_message = "Invalid or malformed JSON received."

    def __init__(self, response: HttpResponseInterface, message: str | None = None, *args) -> None:
        self.response = response
        super().__init__(message, *args)


class InternalInvalidGatewayResponseError(AZBankInternalException):
    default_message = "Invalid gateway response error"

    def __init__(self, message: str | None = None, *args) -> None:
        super().__init__(message, *args)


class InternalInvalidGatewayConfigError(AZBankInternalException):
    default_message = ""

    def __init__(self, message: str | None = None, *args) -> None:
        super().__init__(message, *args)
