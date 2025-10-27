import pytest

from azbankgateways.v3.http_utils.http_client import DefaultHttpClient
from azbankgateways.v3.http_utils.http_request import DefaultHttpRequest
from azbankgateways.v3.http_utils.http_response import DefaultHttpResponse


@pytest.fixture
def http_request_cls():
    return DefaultHttpRequest


@pytest.fixture
def http_response_cls():
    return DefaultHttpResponse


@pytest.fixture
def http_client(http_response_cls):
    return DefaultHttpClient(http_response_cls)
