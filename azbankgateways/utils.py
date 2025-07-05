import json
from urllib import parse
from typing import Optional, List, Tuple, Dict

from azbankgateways.types import DictQuerystring

def get_json(resp):
    """
    Parses the JSON content from an HTTP response.

    :param resp: HTTP response object with a JSON body.
    :return: Parsed JSON data as a Python dictionary.
    """
    return json.loads(resp.content.decode("utf-8"))

def append_querystring(url: str, params: dict) -> str:
    """
    Appends or updates query parameters in a URL.

    :param url: The original URL.
    :param params: Dictionary of parameters to append or update.
    :return: Modified URL with updated query string.
    """
    url_parts = list(parse.urlparse(url))
    query = dict(parse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = parse.urlencode(query)
    return parse.urlunparse(url_parts)

def split_to_dict_querystring(url: str) -> DictQuerystring:
    """
    Splits the query string from a URL and returns the base URL and its query parameters as a dictionary.

    :param url: The original URL with query parameters.
    :return: Tuple of (URL without query string, dictionary of query parameters).
    """
    url_parts = list(parse.urlparse(url))
    query = dict(parse.parse_qsl(url_parts[4]))
    url_parts[4] = ""
    url_parts[5] = ""
    return parse.urlunparse(url_parts), query

def remove_query_param(url: str, param: str) -> str:
    """
    Removes a specific query parameter from the given URL.

    :param url: The URL containing query parameters.
    :param param: The name of the parameter to remove.
    :return: URL without the specified query parameter.
    """
    url_parts = list(parse.urlparse(url))
    query = dict(parse.parse_qsl(url_parts[4]))
    query.pop(param, None)
    url_parts[4] = parse.urlencode(query)
    return parse.urlunparse(url_parts)

def get_query_param(url: str, param: str) -> Optional[str]:
    """
    Retrieves the value of a specific query parameter from the URL.

    :param url: The URL with query parameters.
    :param param: The parameter name to retrieve.
    :return: The value of the parameter, or None if not found.
    """
    query = dict(parse.parse_qsl(parse.urlparse(url).query))
    return query.get(param)

def has_query_param(url: str, param: str) -> bool:
    """
    Checks if a specific query parameter exists in the URL.

    :param url: The URL with query parameters.
    :param param: The parameter name to check.
    :return: True if the parameter exists, False otherwise.
    """
    query = dict(parse.parse_qsl(parse.urlparse(url).query))
    return param in query

def clear_querystring(url: str) -> str:
    """
    Removes all query parameters from the URL.

    :param url: The original URL.
    :return: URL without any query parameters.
    """
    url_parts = list(parse.urlparse(url))
    url_parts[4] = ""
    url_parts[5] = ""
    return parse.urlunparse(url_parts)

def get_all_query_params(url: str) -> List[Tuple[str, str]]:
    """
    Retrieves all query parameters from the URL as a list of tuples.

    :param url: The URL with query parameters.
    :return: List of (key, value) tuples.
    """
    return parse.parse_qsl(parse.urlparse(url).query)

def update_query_param(url: str, key: str, value: str) -> str:
    """
    Updates a single query parameter in the URL.

    :param url: The original URL.
    :param key: Query parameter key.
    :param value: New value for the parameter.
    :return: URL with updated parameter.
    """
    url_parts = list(parse.urlparse(url))
    query = dict(parse.parse_qsl(url_parts[4]))
    query[key] = value
    url_parts[4] = parse.urlencode(query)
    return parse.urlunparse(url_parts)

def filter_query_params(url: str, allowed_keys: List[str]) -> str:
    """
    Filters query parameters, keeping only specified keys.

    :param url: The original URL with query parameters.
    :param allowed_keys: List of keys to retain.
    :return: URL with filtered query parameters.
    """
    url_parts = list(parse.urlparse(url))
    query = dict(parse.parse_qsl(url_parts[4]))
    filtered_query = {k: v for k, v in query.items() if k in allowed_keys}
    url_parts[4] = parse.urlencode(filtered_query)
    return parse.urlunparse(url_parts)

def merge_urls(base_url: str, extra_url: str) -> str:
    """
    Merges query parameters from an extra URL into a base URL.

    :param base_url: The base URL.
    :param extra_url: The URL containing additional query parameters.
    :return: Combined URL.
    """
    _, extra_params = split_to_dict_querystring(extra_url)
    return append_querystring(base_url, extra_params)

def sort_query_params(url: str) -> str:
    """
    Sorts the query parameters of the URL alphabetically by key.

    :param url: The URL to sort.
    :return: URL with sorted query parameters.
    """
    url_parts = list(parse.urlparse(url))
    query = sorted(parse.parse_qsl(url_parts[4]))
    url_parts[4] = parse.urlencode(query)
    return parse.urlunparse(url_parts)
 
