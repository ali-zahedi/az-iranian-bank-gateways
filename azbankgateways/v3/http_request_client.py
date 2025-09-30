import json
from typing import Any, Dict

import requests

from azbankgateways.v3.exceptions import (
    BankGatewayConnectionError,
    BankGatewayHttpResponseError,
)
from azbankgateways.v3.interfaces import (
    HttpClientInterface,
    HttpMethod,
    HttpRequestInterface,
    HttpResponseInterface,
    MessageServiceInterface,
    MessageType,
)


class HttpRequest(HttpRequestInterface):
    def __init__(
        self, method: HttpMethod, url: str, headers: dict[str, Any], data: dict[str, Any], timeout: int
    ):
        self.__method = method
        self.__url = url
        self.__headers = headers
        self.__data = data
        self.__timeout = timeout

    @property
    def http_method(self) -> HttpMethod:
        return self.__method

    @property
    def url(self) -> str:
        return self.__url

    @property
    def headers(self) -> Dict[str, Any]:
        return self.__headers

    @property
    def data(self) -> Dict[str, Any]:
        return self.__data

    @property
    def is_json(self) -> bool:
        return self.headers.get("Content-Type") == "application/json"

    @property
    def timeout(self) -> int:
        return self.__timeout


class HttpResponse(HttpResponseInterface):
    def __init__(self, status_code: int, headers: dict[str, Any], body: Any):
        self.__status_code = status_code
        self.__headers = headers
        self.__body = body

    @property
    def status_code(self) -> int:
        return self.__status_code

    @property
    def headers(self) -> Dict[str, Any]:
        return self.__headers

    @property
    def body(self) -> Any:
        return self.__body

    @property
    def is_json(self) -> bool:
        return self.headers.get('Content-Type') == 'application/json'

    def json(self) -> Dict[str, Any]:
        if not self.is_json:
            raise BankGatewayHttpResponseError()
        try:
            return json.loads(self.body)
        except (TypeError, json.JSONDecodeError):
            raise BankGatewayHttpResponseError()

    @property
    def ok(self) -> bool:
        return self.status_code in range(200, 400)


class HttpRequestClient(HttpClientInterface):
    def __init__(
        self, message_service: MessageServiceInterface, http_response_cls: type[HttpResponseInterface]
    ):
        self.__message_service = message_service
        self.__http_response_cls = http_response_cls

    def send(self, request: HttpRequestInterface) -> HttpResponseInterface:
        data = json.dumps(request.data) if request.is_json else request.data

        try:
            response = requests.request(
                request.http_method.value,
                request.url,
                data=data,
                headers=request.headers,
                timeout=request.timeout,
            )
        except requests.exceptions.Timeout as e:
            raise BankGatewayConnectionError(
                self.__message_service.generate_message(
                    MessageType.TIMEOUT_ERROR,
                    context={'request': request, 'exception': e},
                )
            )
        except requests.exceptions.ConnectionError as e:
            raise BankGatewayConnectionError(
                self.__message_service.generate_message(
                    MessageType.CONNECTION_ERROR,
                    context={'request': request, 'exception': e},
                )
            )
        except requests.exceptions.RequestException as e:
            raise BankGatewayConnectionError(
                self.__message_service.generate_message(
                    MessageType.CONNECTION_ERROR,
                    context={'request': request, 'exception': e},
                )
            )
        return self.__http_response_cls(
            status_code=response.status_code,
            headers=response.headers,
            body=response.content,
        )
