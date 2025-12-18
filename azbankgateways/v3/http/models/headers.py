from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from requests.structures import CaseInsensitiveDict

from azbankgateways.v3.interfaces import HTTPHeadersInterface


if TYPE_CHECKING:
    from azbankgateways.v3.typing import HTTPHeaders as HTTPHeadersType


class HTTPHeaders(HTTPHeadersInterface):
    def __init__(self, headers: HTTPHeadersType):
        self._store = CaseInsensitiveDict(headers)

    def get(self, name: str, default: Any | None = None) -> Any:
        return self._store.get(name)

    def to_dict(self) -> HTTPHeadersType:
        return dict(self._store)

    @property
    def is_json(self) -> bool:
        return cast(str | None, self.get("Content-Type")) == "application/json"
