from __future__ import annotations

import json
from importlib.resources import files
from typing import TYPE_CHECKING

import parametrize_from_file as pff
import requests

from azbankgateways.v3.http import URL
from azbankgateways.v3.interfaces import (
    HTTPClientInterface,
    HTTPHeadersInterface,
    HTTPMethod,
    HTTPRequestInterface,
)


if TYPE_CHECKING:
    from responses import RequestsMock
    from syrupy import SnapshotAssertion

    from azbankgateways.v3.testing.syrupy.fixtures import ExceptionAssertion

TEST_DATA = json.load((files("tests.v3.http") / "test_client.json").open())


@pff.parametrize(schema=pff.defaults(**TEST_DATA["defaults"]["test_send"]))
def test_send(
    responses: RequestsMock,
    http_headers_class: type[HTTPHeadersInterface],
    http_request_class: type[HTTPRequestInterface],
    http_client: HTTPClientInterface,
    method: str,
    url: str,
    timeout: int,
    status_code: int | None,
    response_headers: dict[str, str],
    data: str,
    exception: str | None,
    snapshot: SnapshotAssertion,
    capture_exception: ExceptionAssertion,
) -> None:
    responses.add(
        method=method,
        url=url,
        body=data if exception is None else getattr(requests.exceptions, exception)(),
        status=status_code,
        headers=response_headers,
    )

    http_request = http_request_class(
        http_method=HTTPMethod[method],
        url=URL(url),
        timeout=timeout,
        headers=http_headers_class({}),
        data={},
    )

    with capture_exception():
        response = http_client.send(http_request)

        assert response.status_code == snapshot(name="expected_status_code")
        assert response.ok == snapshot(name="expected_ok")
        assert response.json() == snapshot(name="expected_body")
