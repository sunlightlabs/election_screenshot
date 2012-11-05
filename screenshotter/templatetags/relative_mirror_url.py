import urlparse
import pytz
from django import template
from utils import abbrev_isoformat
from django.conf import settings

register = template.Library()

@register.filter
def relative_mirror_url(mirror):
    tz = pytz.timezone(settings.TIME_ZONE)
    timestamp = abbrev_isoformat(mirror.timestamp.astimezone(tz))
    print timestamp
    parsed = urlparse.urlparse(mirror.election_url.url)
    if parsed.path == '/':
        fixedpath = "index.html"
    else:
        fixedpath = parsed.path.strip('/')
    return '{state}/{sha1}/{timestamp}/{netloc}/{path}'.format(state=mirror.election_url.state,
                                                               sha1=mirror.election_url.url_sha1,
                                                               timestamp=timestamp,
                                                               netloc=parsed.netloc,
                                                               path=fixedpath)
