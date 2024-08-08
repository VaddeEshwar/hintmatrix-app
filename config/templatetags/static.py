"""
static template tag, post pend with BPC query string for all URLS.
"""
from urllib.parse import (
    urlencode,
    urlparse,
    parse_qs
)

from django.conf import settings
from django.templatetags.static import StaticNode

old_render = StaticNode.render


def static_bpc_render(cls, context):
    """
    Override existing static url method to use BPC query parameter.
    """
    url = old_render(cls, context)
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    bpc = getattr(settings, "BPC", 3)
    query_params[b"BPC"] = bpc
    query = urlencode(query_params)

    return f"{parsed_url.geturl()}?{query}"


StaticNode.render = static_bpc_render
