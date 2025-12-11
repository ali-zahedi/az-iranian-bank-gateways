from typing import Any

from requests.structures import CaseInsensitiveDict

from azbankgateways.v3.interfaces import HttpHeadersInterface


class HttpHeaders(HttpHeadersInterface):
    def __init__(self, headers: dict[str, Any]):
        self._store = CaseInsensitiveDict(headers)

    def get(self, name: str, default: Any | None = None) -> Any:
        return self._store.get(name)

    def to_dict(self) -> dict[str, Any]:
        return dict(self._store)

    @property
    def is_json(self) -> bool:
        return self.get("Content-Type") == "application/json"
