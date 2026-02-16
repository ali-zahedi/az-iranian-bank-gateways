from __future__ import annotations

from typing import TYPE_CHECKING

import parametrize_from_file as pff
from syrupy.assertion import SnapshotAssertion


if TYPE_CHECKING:
    from azbankgateways.v3.interfaces import HTTPHeadersInterface


def test_get_header_case_insensitive(http_headers_class: type[HTTPHeadersInterface]) -> None:
    headers = http_headers_class({'Content-Type': 'application/json'})

    assert headers.get('content-type') == headers.get('Content-Type') == 'application/json'


@pff.parametrize  # type: ignore[untyped-decorator]
def test_headers(
    http_headers_class: type[HTTPHeadersInterface],
    headers_data: dict[str, str],
    snapshot: SnapshotAssertion,
) -> None:
    headers = http_headers_class(headers_data)

    assert headers.to_dict() == snapshot(name="expected_headers_dict")
    assert headers.is_json == snapshot(name="expected_is_json")
