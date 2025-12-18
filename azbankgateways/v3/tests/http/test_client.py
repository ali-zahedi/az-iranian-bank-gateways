from __future__ import annotations

from typing import TYPE_CHECKING

from azbankgateways.v3.http import URL, HTTPClient, HTTPResponse
from azbankgateways.v3.interfaces import HTTPMethod


if TYPE_CHECKING:
    from typing import Any

    from azbankgateways.v3.interfaces import (
        HTTPHeadersInterface,
        HTTPRequestInterface,
        HTTPResponseInterface,
    )


def test_send(
    http_headers_class: type[HTTPHeadersInterface],
    http_response_class: type[HTTPResponseInterface],
    http_request_class: type[HTTPRequestInterface],
    responses: Any,
) -> None:
    client = HTTPClient(http_response_class, http_headers_class)
    http_request = http_request_class(
        http_method=HTTPMethod.POST,
        url=URL("https://az.bank/test/"),
        timeout=10,
        headers=http_headers_class({}),
        data={},
    )
    responses.add(
        responses.POST,
        "https://az.bank/test/",
        json={"success": True},
        status=200,
    )

    response = client.send(http_request)

    assert isinstance(response, HTTPResponse)
    assert response.status_code == 200
    assert response.body == b'{"success": true}'
    assert response.headers.to_dict() == {"Content-Type": "application/json"}
