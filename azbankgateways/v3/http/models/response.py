from __future__ import annotations

import json
from typing import Any

from azbankgateways.v3.exceptions.internal import InternalInvalidJsonError
from azbankgateways.v3.interfaces import HttpHeadersInterface, HttpResponseInterface


class HttpResponse(HttpResponseInterface):
    def __init__(self, status_code: int, headers: HttpHeadersInterface, body: Any) -> None:
        self._status_code = status_code
        self._headers = headers or {}
        self._body = body

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def headers(self) -> HttpHeadersInterface:
        return self._headers

    @property
    def body(self) -> Any:
        return self._body

    @property
    def is_json(self) -> bool:
        return self.headers.is_json

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
