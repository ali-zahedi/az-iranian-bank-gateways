from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional


if TYPE_CHECKING:
    from azbankgateways.v3.http_utils import URL


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

    @abstractmethod
    def __init__(
        self,
        http_method: HttpMethod,
        url: URL,
        timeout: int,
        headers: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
    ):
        raise NotImplementedError()

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
    def url(self) -> URL:
        """
        Provides the full URL to which the request should be made.

        :return: A string representing the URL.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def headers(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves the headers to be included in the redirect request.

        :return: A dictionary containing header key-value pairs.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def data(self) -> Optional[Dict[str, Any]]:
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

    @property
    @abstractmethod
    def timeout(self) -> int:
        """
        Specifies the maximum duration (in seconds) the request should wait
        for a response before timing out.

        :return: An integer representing the timeout duration in seconds.
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

    @abstractmethod
    def __init__(self, status_code: int, headers: Dict[str, Any], body: Any):
        raise NotImplementedError()

    @property
    @abstractmethod
    def status_code(self) -> int:
        """
        The HTTP status code returned by the server.

        :return: Integer representing the HTTP status code (e.g., 200, 404, 500).
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def headers(self) -> Dict[str, Any]:
        """
        The HTTP headers included in the response.

        :return: Dictionary containing header names and values.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def body(self) -> Any:
        """
        The raw body content of the HTTP response.

        This may be a string, bytes, or parsed object depending on implementation.

        :return: The raw or parsed content of the response body.
        """
        raise NotImplementedError()

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


CallbackURLType = Callable[[OrderDetails], 'URL']


class PaymentGatewayConfigInterface(ABC):
    """Payment Gateway configuration interface."""

    # TODO: Ensure all subclasses of PaymentGatewayConfigInterface are
    #  decorated with @dataclass(frozen=True, slots=True).


class HttpClientInterface(ABC):
    @abstractmethod
    def __init__(self, http_response_cls: type[HttpResponseInterface]):
        raise NotImplementedError()

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
    @classmethod
    @abstractmethod
    def create(
        cls,
        config: PaymentGatewayConfigInterface,
        message_service: MessageServiceInterface,
        http_client: HttpClientInterface,
        http_request_cls: type[HttpRequestInterface],
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
    def create_payment_request(self, order_details: OrderDetails) -> HttpRequestInterface:
        # TODO: add proper doc string
        raise NotImplementedError()

    @abstractmethod
    def check_minimum_amount(self, order_details: OrderDetails) -> None:
        raise NotImplementedError
