from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional


if TYPE_CHECKING:
    from azbankgateways.v3.http_utils.url import URL


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
    REQUEST_ERROR = 'request_error'
    REJECTED_PAYMENT = 'rejected_payment'
    MINIMUM_AMOUNT = 'minimum_amount'
    RESPONSE_IS_NOT_JSON = 'response_is_not_json'
    JSON_DECODE_ERROR = 'json_decode_error'


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


class MessageServiceInterface(ABC):
    @abstractmethod
    def generate_message(self, key: MessageType, context: Dict[str, Any]) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_required_parameters(self, key: MessageType) -> Optional[list]:
        raise NotImplementedError()


class HttpRequestInterface(ABC):
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
    def is_json(self) -> bool:
        """
        Indicates if the data should be sent as JSON or form data.

        :return: True if the data should be sent as JSON, otherwise False.
        """
        raise NotImplementedError()


class HttpResponseInterface(ABC):
    """
    An interface representing the structure of an HTTP response.

    Implementations must provide consistent access to HTTP status, headers,
    body content, and content type.
    This abstraction allows response handling to remain decoupled from
    specific HTTP client libraries or transport layers.

    Common use cases include payment gateway responses, API integrations,
    or testing environments where HTTP behavior is mocked.
    """

    @property
    @abstractmethod
    def ok(self) -> bool:
        """
        Indicates whether the HTTP response is considered successful.

        Typically, returns True for status codes in the 200–299 range.

        :return: True if the status_code represents a successful response, else False.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def is_json(self) -> bool:
        """
        Indicates whether the response body contains JSON data.

        :return: True if the response is JSON, otherwise False.
        """
        raise NotImplementedError()

    @abstractmethod
    def json(self) -> Dict[str, Any]:
        """
        Parses and returns the response body as a JSON object if available.

        :return: Dictionary representing the JSON body.
        :raises BankGatewayHttpResponseError: If the body cannot be parsed as JSON.
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
    description: Optional[str] = None


CallbackURLType = Callable[[OrderDetails], "URL"]


class PaymentGatewayConfigInterface(ABC):
    """Payment Gateway configuration interface."""

    # TODO: Ensure all subclasses of PaymentGatewayConfigInterface are
    #  decorated with @dataclass(frozen=True, slots=True).


class HttpClientInterface(ABC):
    @abstractmethod
    def send(
        self,
        http_request: HttpRequestInterface,
    ) -> HttpResponseInterface:
        """
        Send an HTTP request and return the corresponding response.

        Implementations must perform the network call and return a response object conforming to HttpResponseInterface.

        Args:
            http_request (HttpRequestInterface): The request to send.

        Returns:
            HttpResponseInterface: The response associated with the request.
        """
        raise NotImplementedError()


class ProviderInterface(ABC):
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
    def create_payment_request(self, order_details: OrderDetails) -> HttpRequestInterface:
        # TODO: add proper doc string
        raise NotImplementedError()

    @abstractmethod
    def check_minimum_amount(self, order_details: OrderDetails) -> None:
        raise NotImplementedError
