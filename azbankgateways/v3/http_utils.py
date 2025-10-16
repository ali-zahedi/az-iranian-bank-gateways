import json
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import requests

from azbankgateways.v3.exceptions.internal import (
    InternalConnectionError,
    InternalInvalidJsonError,
)
from azbankgateways.v3.interfaces import (
    HttpClientInterface,
    HttpMethod,
    HttpRequestInterface,
    HttpResponseInterface,
)


@dataclass(frozen=True, slots=True)
class URL:
    value: str

    def __post_init__(self) -> None:
        parsed = urlparse(self.value)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL: {self.value}")

        normalized = self.value if self.value.endswith("/") else self.value + "/"
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"URL({self.value!r})"

    def join(self, path: str) -> str:
        """Join a relative path to this base URL"""
        return self.value.rstrip("/") + "/" + path.lstrip("/")


class HttpRequest(HttpRequestInterface):
    def __init__(
        self,
        http_method: HttpMethod,
        url: URL,
        timeout: int,
        headers: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
    ):
        self.__http_method = http_method
        self.__url = url
        self.__headers = headers
        self.__data = data
        self.__timeout = timeout

    @property
    def http_method(self) -> HttpMethod:
        return self.__http_method

    @property
    def url(self) -> URL:
        return self.__url

    @property
    def headers(self) -> Optional[Dict[str, Any]]:
        return self.__headers

    @property
    def data(self) -> Optional[Dict[str, Any]]:
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
            raise InternalInvalidJsonError(self, message="Response content-type is not JSON.")
        try:
            return json.loads(self.body)
        except (TypeError, json.JSONDecodeError):
            raise InternalInvalidJsonError(self, message="Failed to decode response body as JSON.")

    @property
    def ok(self) -> bool:
        return self.status_code in range(200, 400)


class HttpRequestClient(HttpClientInterface):
    def __init__(self, http_response_cls: type[HttpResponseInterface]):
        self.__http_response_cls = http_response_cls

    def send(self, request: HttpRequestInterface) -> HttpResponseInterface:
        data = json.dumps(request.data) if request.is_json else request.data

        try:
            response = requests.request(
                request.http_method.value,
                str(request.url),
                data=data,
                headers=request.headers,
                timeout=request.timeout,
            )
        except requests.exceptions.Timeout as e:
            raise InternalConnectionError(request, exception=e)
        except requests.exceptions.ConnectionError as e:
            raise InternalConnectionError(request, exception=e)
        except requests.exceptions.RequestException as e:
            raise InternalConnectionError(request, exception=e)
        return self.__http_response_cls(
            status_code=response.status_code,
            headers=response.headers,
            body=response.content,
        )
