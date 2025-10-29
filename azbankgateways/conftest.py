import pytest

from azbankgateways.v3.http import (
    DefaultHttpClient,
    DefaultHttpRequest,
    DefaultHttpResponse,
)


@pytest.fixture
def http_request_cls():
    return DefaultHttpRequest


@pytest.fixture
def http_response_cls():
    return DefaultHttpResponse


@pytest.fixture
def http_client(http_response_cls):
    return DefaultHttpClient(http_response_cls)
