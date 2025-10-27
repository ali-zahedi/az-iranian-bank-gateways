from __future__ import annotations

import json
from abc import ABCMeta, abstractmethod
from typing import Any, Type, TypeVar

from azbankgateways.v3.exceptions.internal import InternalInvalidJsonError
from azbankgateways.v3.interfaces import HttpResponseInterface


T = TypeVar("T", bound="HttpResponseInterface")


class HttpResponseMeta(ABCMeta):
    def __call__(
        cls: Type[T],
        status_code: int,
        headers: dict[str, Any],
        body: Any,
    ) -> T:
        return super().__call__(status_code=status_code, headers=headers, body=body)


class HttpResponse(HttpResponseInterface, metaclass=HttpResponseMeta):
    def __init__(self, status_code: int, headers: dict[str, Any], body: Any) -> None:
        self.status_code = status_code
        self.headers = headers or {}
        self.body = body

    @property
    @abstractmethod
    def is_json(self) -> bool:
        raise NotImplementedError("Subclasses must implement the `is_json` property.")

    @abstractmethod
    def json(self) -> dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the `json` method.")

    @property
    @abstractmethod
    def ok(self) -> bool:
        raise NotImplementedError("Subclasses must implement the `ok` property.")


class DefaultHttpResponse(HttpResponse):
    @property
    def is_json(self) -> bool:
        return self.headers.get('Content-Type') == 'application/json'

    def json(self) -> dict[str, Any]:
        if not self.is_json:
            raise InternalInvalidJsonError(self, message="Response content-type is not JSON.")
        try:
            return json.loads(self.body)
        except (TypeError, ValueError, json.JSONDecodeError) as e:
            raise InternalInvalidJsonError(
                self, message=f"Failed to decode response body as JSON: {e}"
            ) from e

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400
