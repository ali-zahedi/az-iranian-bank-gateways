from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, Literal, Optional


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


class RedirectRequestInterface(ABC):
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
    amount: Decimal
    tracking_code: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    order_id: Optional[str] = None
    currency: Literal["IRT", "IRR"] = "IRT"


CallbackURLType = Callable[[OrderDetails], str]


class PaymentGatewayConfigInterface(ABC):
    """Payment Gateway configuration interface."""


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
        order_details: OrderDetails,
    ):
        raise NotImplementedError()

    @property
    @abstractmethod
    def currency(self) -> Currency:
        """
        Defines the currency in which the payment will be made.
        This should return a value from the Currency enum, representing the type of currency being used
        (e.g., IRT, IRR).

        :return: An instance of Currency representing the payment currency.
        """
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
    def get_request_pay(self) -> RedirectRequestInterface:
        # TODO: add proper doc string
        raise NotImplementedError()


class ResponseInterface(ABC):
    @property
    @abstractmethod
    def status_code(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def json(self) -> Dict[str, Any]:
        raise NotImplementedError()

    @abstractmethod
    def raise_for_status(self):
        raise NotImplementedError()


class RequestInterface(ABC):
    """
    An interface for making HTTP requests, providing methods for various HTTP methods
    (e.g., GET, POST, PUT, DELETE, etc.) and support for SOAP requests.
    It defines abstract methods that should be implemented by subclasses to handle
    the specifics of HTTP request handling, error handling, and response handling.
    """

    class RequestException(IOError):
        pass

    class Timeout(RequestException):
        pass

    class ConnectionError(RequestException):
        pass

    class HTTPError(RequestException):
        pass

    @abstractmethod
    def request(
        self,
        method: HttpMethod,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ResponseInterface:
        """
        Send an HTTP request using the specified method.

        Args:
            method (HttpMethod): The HTTP method to use (e.g., GET, POST, PUT).
            url (str): The URL to send the request to.
            data (Optional[Any]): The request payload (typically for POST, PUT, PATCH).
            json (Optional[Dict[str, Any]]): The JSON payload to be sent in the request body.
            **kwargs: Additional request parameters (e.g., headers, query params).

        Returns:
            ResponseInterface: The response received from the request.

        Raises:
            Timeout: If the request times out.
            ConnectionError: If there is a connection-related error.
            HTTPError: If an HTTP error occurs.
        """
        raise NotImplementedError()

    def soap_request(
        self, url: str, soap_action: str, xml: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> ResponseInterface:
        if headers is None:
            headers = {}
        headers.update({'Content-Type': 'text/xml; charset=utf-8', 'SOAPAction': soap_action})
        return self.post(url, data=xml, headers=headers, **kwargs)

    def post(
        self, url: str, data: Optional[Any] = None, json: Optional[Dict[str, Any]] = None, **kwargs
    ) -> ResponseInterface:
        return self.request(HttpMethod.POST, url, data, json, **kwargs)

    def put(
        self, url: str, data: Optional[Any] = None, json: Optional[Dict[str, Any]] = None, **kwargs
    ) -> ResponseInterface:
        return self.request(HttpMethod.POST, url, data, json, **kwargs)

    def get(
        self, url: str, data: Optional[Any] = None, json: Optional[Dict[str, Any]] = None, **kwargs
    ) -> ResponseInterface:
        return self.request(HttpMethod.POST, url, data, json, **kwargs)

    def delete(
        self, url: str, data: Optional[Any] = None, json: Optional[Dict[str, Any]] = None, **kwargs
    ) -> ResponseInterface:
        return self.request(HttpMethod.POST, url, data, json, **kwargs)

    def patch(
        self, url: str, data: Optional[Any] = None, json: Optional[Dict[str, Any]] = None, **kwargs
    ) -> ResponseInterface:
        return self.request(HttpMethod.POST, url, data, json, **kwargs)

    def head(
        self, url: str, data: Optional[Any] = None, json: Optional[Dict[str, Any]] = None, **kwargs
    ) -> ResponseInterface:
        return self.request(HttpMethod.POST, url, data, json, **kwargs)

    def options(
        self, url: str, data: Optional[Any] = None, json: Optional[Dict[str, Any]] = None, **kwargs
    ) -> ResponseInterface:
        return self.request(HttpMethod.POST, url, data, json, **kwargs)
