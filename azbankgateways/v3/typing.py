from __future__ import annotations

from typing import Callable, TypeAlias

from azbankgateways.v3.http import URL
from azbankgateways.v3.interfaces import OrderDetails


CallbackURL = Callable[[OrderDetails], URL]


HTTPHeaders: TypeAlias = dict[str, str]


JSONScalar: TypeAlias = str | int | float | bool | None
JSONArray: TypeAlias = list["JSONValue"]
JSONObject: TypeAlias = dict[str, "JSONValue"]
JSONValue: TypeAlias = JSONScalar | JSONArray | JSONObject
JSONDocument: TypeAlias = JSONArray | JSONObject
