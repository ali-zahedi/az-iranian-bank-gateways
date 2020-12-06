import json
from urllib import parse


def get_json(resp):
    """
    :param response:returned response as json when sending a request
    using 'requests' module.

    :return:response's content with json format
    """

    return json.loads(resp.content.decode('utf-8'))


def append_querystring(url: str, params: dict) -> str:
    url_parts = list(parse.urlparse(url))
    query = dict(parse.parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = parse.urlencode(query)

    return parse.urlunparse(url_parts)
