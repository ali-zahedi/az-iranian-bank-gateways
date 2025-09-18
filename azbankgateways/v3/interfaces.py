from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, Optional


# TODO: abstract
class Currency(Enum):
    IRT = 'IRT'
    IRR = 'IRR'


# TODO: abstract
class BankType(Enum):
    pass


# TODO: abstract
class MessageType(Enum):
    DESCRIPTION = 'description'
    TIMEOUT_ERROR = 'timeout_error'
    CONNECTION_ERROR = 'connection_error'
    REJECTED_PAYMENT = 'rejected_payment'
    MINIMUM_AMOUNT = 'minimum_amount'


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class BankEntityInterface(ABC):
    @abstractmethod
    def persist(self):
        raise NotImplementedError()


class RequestInterface(ABC):
    """
    An interface for defining the structure of a redirect request, typically used to
     manage payment redirections or external API redirects.
    This interface ensures that any implementing class provides consistent behavior for handling HTTP methods,
     URLs, headers, data, and content type.

    This is particularly useful for payment gateways or third-party integrations where the details of the HTTP request
     (such as the method, headers, or body) need to be abstracted and standardized across different implementations.
    """

    @property
    @abstractmethod
    def http_method(self) -> HttpMethod:
        """
        Determines the HTTP method (e.g., GET, POST) to be used for the redirect request.

        :return: An instance of HttpMethod indicating the HTTP method.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def url(self) -> str:
        """
        Provides the full URL to which the request should be made.

        :return: A string representing the URL.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def headers(self) -> Dict[str, Any]:
        """
        Retrieves the headers to be included in the redirect request.

        :return: A dictionary containing header key-value pairs.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def data(self) -> Dict[str, Any]:
        """
        Retrieves the body data content for the redirect request.
        Note: For GET requests, the data should typically be empty.

        :return: A dictionary containing the body data or parameters.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def is_json(self) -> bool:
        """
        Indicates if the data should be sent as JSON or form data.

        :return: True if the data should be sent as JSON, otherwise False.
        """
        raise NotImplementedError()


@dataclass
class OrderDetails:
    """
    Represents order payment details.

    Note:
        `amount` is always specified in IRR.
    """

    amount: Decimal
    tracking_code: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    order_id: Optional[str] = None


CallbackURLType = Callable[[OrderDetails], str]


class PaymentGatewayConfigInterface(ABC):
    """Payment Gateway configuration interface."""

    # TODO: Ensure all subclasses of PaymentGatewayConfigInterface are
    #  decorated with @dataclass(frozen=True, slots=True).


class MessageServiceInterface(ABC):
    @abstractmethod
    def generate_message(self, key: MessageType, context: Dict[str, Any]) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_required_parameters(self, key: MessageType) -> Optional[list]:
        raise NotImplementedError()


class ProviderInterface(ABC):
    @abstractmethod
    def __init__(
        self,
        config: PaymentGatewayConfigInterface,
        message_service: MessageServiceInterface,
    ):
        raise NotImplementedError()

    @property
    @abstractmethod
    def minimum_amount(self) -> Decimal:
        """
        Specifies the minimum payment amount required for the payment process.
        This value should be returned as a Decimal to maintain precision in financial calculations.

        :return: A Decimal value representing the minimum payment amount.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_request_pay(self, order_details: OrderDetails) -> RequestInterface:
        # TODO: add proper doc string
        raise NotImplementedError()
