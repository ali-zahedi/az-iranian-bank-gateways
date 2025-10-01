import json
from urllib import parse

from django.conf import settings
from django.urls import reverse

from azbankgateways.types import DictQuerystring


def get_json(resp):
    """
    :param response:returned response as json when sending a request
    using 'requests' module.

    :return:response's content with json format
    """

    return json.loads(resp.content.decode("utf-8"))


def append_querystring(url: str, params: dict) -> str:
    url_parts = list(parse.urlparse(url))
    query = dict(parse.parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = parse.urlencode(query)

    return parse.urlunparse(url_parts)


def split_to_dict_querystring(url: str) -> DictQuerystring:
    url_parts = list(parse.urlparse(url))
    query = dict(parse.parse_qsl(url_parts[4]))

    url_parts[4] = ""
    url_parts[5] = ""

    return parse.urlunparse(url_parts), query


def build_full_url(viewname: str, *args, **kwargs):
    """
    Build a full absolute URL including domain if Sites framework is available.
    Falls back to relative path if no site is configured.
    """
    # Generate the path part
    path = reverse(viewname, args=args, kwargs=kwargs)

    # Try to use django.contrib.sites if installed
    if "django.contrib.sites" in settings.INSTALLED_APPS:
        try:
            from django.contrib.sites.models import Site

            site = Site.objects.get_current()
            if site and site.domain:
                protocol = getattr(settings, "DEFAULT_PROTOCOL", "https")
                return f"{protocol}://{site.domain}{path}"
        except Exception:
            # Any issue with Sites, just return relative path
            pass

    # Fallback: return only relative path
    return path
