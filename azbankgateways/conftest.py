import pytest

from azbankgateways.v3.http import HttpClient, HttpRequest, HttpResponse


@pytest.fixture
def http_request_class():
    return HttpRequest


@pytest.fixture
def http_response_class():
    return HttpResponse


@pytest.fixture
def http_client(http_response_class):
    return HttpClient(http_response_class)
