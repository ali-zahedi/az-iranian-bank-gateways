from azbankgateways.v3.http import HttpHeaders


def test_get():
    headers = HttpHeaders({'Content-Type': 'application/json'})

    assert headers.get('Content-Type') == 'application/json'
    assert headers.get('content-type') == 'application/json'  # case-insensitive


def test_to_dict():
    headers = HttpHeaders({'Content-Type': 'application/json', 'ACCEPT': '*/*'})

    assert headers.to_dict() == {'Content-Type': 'application/json', 'ACCEPT': '*/*'}


def test_is_json():
    headers = HttpHeaders({'Content-Type': 'application/json'})

    assert headers.is_json is True


def test_is_not_json():
    headers = HttpHeaders({'Content-Type': 'text/plain'})

    assert headers.is_json is False
