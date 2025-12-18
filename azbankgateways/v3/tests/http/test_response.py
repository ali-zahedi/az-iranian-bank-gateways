from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from azbankgateways.v3.exceptions.internal import InternalInvalidJsonError
from azbankgateways.v3.http import HTTPResponse


if TYPE_CHECKING:
    from azbankgateways.v3.interfaces import HTTPHeadersInterface
    from azbankgateways.v3.typing import HTTPHeaders as HTTPHeadersType


@pytest.mark.parametrize(
    "status_code,expected_ok",
    [
        (201, True),
        (404, False),
        (200, True),
    ],
)
def test_ok(status_code: int, expected_ok: bool, http_headers_class: type[HTTPHeadersInterface]) -> None:
    response = HTTPResponse(status_code=status_code, headers=http_headers_class({}), body={})

    assert response.ok is expected_ok


@pytest.mark.parametrize(
    "headers,body",
    [
        ({'content-type': 'application/json'}, 'Incorrect Json'),
        ({'content-type': 'text/xml'}, 'Incorrect Json'),
    ],
)
def test_invalid_json(
    headers: HTTPHeadersType, body: str, http_headers_class: type[HTTPHeadersInterface]
) -> None:
    response = HTTPResponse(status_code=200, headers=http_headers_class(headers), body=body)

    with pytest.raises(InternalInvalidJsonError):
        response.json()


def test_json(http_headers_class: type[HTTPHeadersInterface]) -> None:
    response = HTTPResponse(
        status_code=200,
        headers=http_headers_class({'content-type': 'application/json'}),
        body='{"price": 100}',
    )

    assert response.json() == {'price': 100}
