import urllib2, base64
import json
from time import time

from plone.memoize.ram import cache

from .config import ADDTHIS_DOMAIN, ADDTHIS_PUBID, ADDTHIS_PERIOD, \
     ADDTHIS_USERNAME, ADDTHIS_PASSWORD, ADDTHIS_CACHE_TIME


def _addthis_mostliked_cache_key(fun, *args, **kw):
    timeout = time() // ADDTHIS_CACHE_TIME
    return (timeout,)

@cache(_addthis_mostliked_cache_key)
def _addThisShared():
    """Returns top shared urls from addthis.com"""
    # TODO: handle pagination
    url = 'https://api.addthis.com/analytics/1.0/pub/shares/url.json?' \
        'domain=%s&pubid=%s&period=%s&service=facebook_like' % (ADDTHIS_DOMAIN,
            ADDTHIS_PUBID, ADDTHIS_PERIOD)

    request = urllib2.Request(url)
    auth = base64.encodestring('%s:%s' % (ADDTHIS_USERNAME,
        ADDTHIS_PASSWORD)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % auth)
    return json.loads(urllib2.urlopen(request).read())

def getAddThisSharedURLs():
    try:
        urls = _addThisShared()
    except Exception:
        return []
    else:
        return urls
