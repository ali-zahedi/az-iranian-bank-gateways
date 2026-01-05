from __future__ import annotations

import json
from importlib.resources import files
from typing import TYPE_CHECKING

import parametrize_from_file as pff
from syrupy import SnapshotAssertion


if TYPE_CHECKING:
    from azbankgateways.v3.interfaces import HTTPHeadersInterface, HTTPResponseInterface
    from azbankgateways.v3.testing.syrupy.fixtures import ExceptionAssertion

TEST_DATA = json.load((files("tests.v3.http") / "test_response.json").open())


@pff.parametrize(schema=pff.defaults(**TEST_DATA["defaults"]["test_response"]))
def test_response(
    http_headers_class: type[HTTPHeadersInterface],
    http_response_class: type[HTTPResponseInterface],
    status_code: int,
    headers: dict[str, str],
    body: str,
    snapshot: SnapshotAssertion,
    capture_exception: ExceptionAssertion,
):
    response = http_response_class(
        status_code=status_code,
        headers=http_headers_class(headers),
        body=body,
    )

    with capture_exception():
        assert response.json() == snapshot(name="expected_json")
        assert response.ok == snapshot(name="expected_ok")
