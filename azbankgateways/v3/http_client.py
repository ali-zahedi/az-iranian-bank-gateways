from typing import Any, Dict, Optional

import requests

from azbankgateways.v3.interfaces import HttpMethod, RequestInterface, ResponseInterface


class Response(ResponseInterface):
    def __init__(self, response: requests.Response):
        self.__response = response

    @property
    def status_code(self) -> int:
        return self.__response.status_code

    def json(self) -> Dict[str, Any]:
        return self.__response.json()

    def raise_for_status(self):
        try:
            self.__response.raise_for_status()
        except requests.HTTPError as e:
            raise RequestInterface.HTTPError(e)


class Request(RequestInterface):
    def request(
        self,
        method: HttpMethod,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ResponseInterface:
        try:
            response = requests.request(method.value, url, data=data, json=json, **kwargs)
        except requests.exceptions.Timeout as e:
            raise RequestInterface.Timeout(e) from e
        except requests.exceptions.ConnectionError as e:
            raise RequestInterface.ConnectionError(e) from e

        return Response(response)
