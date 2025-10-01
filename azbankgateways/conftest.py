import pytest

from azbankgateways.v3.http_utils import HttpRequest, HttpRequestClient, HttpResponse


@pytest.fixture
def http_client(http_response_cls):
    return HttpRequestClient(http_response_cls)


@pytest.fixture
def http_request_cls():
    return HttpRequest


@pytest.fixture
def http_response_cls():
    return HttpResponse
