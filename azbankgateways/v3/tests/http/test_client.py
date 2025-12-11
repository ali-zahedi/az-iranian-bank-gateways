from azbankgateways.v3.http import URL, HttpClient, HttpResponse
from azbankgateways.v3.interfaces import HttpMethod


def test_send(http_headers_class, http_response_class, http_request_class, responses):
    client = HttpClient(http_response_class, http_headers_class)
    http_request = http_request_class(
        http_method=HttpMethod.POST,
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

    assert isinstance(response, HttpResponse)
    assert response.status_code == 200
    assert response.body == b'{"success": true}'
    assert response.headers.to_dict() == {"Content-Type": "application/json"}
