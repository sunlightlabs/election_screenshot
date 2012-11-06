import os
import math
import time
import logbook
import pytz
from optparse import make_option
from django.core.management.base import BaseCommand
from screenshotter.models import ElectionUrl
from screenshotter.wget import mirror_url
from utils import configure_log_handler
from django.conf import settings


_script_ = (os.path.basename(__file__)
            if __name__ == "__main__"
            else __name__)
log = logbook.Logger(_script_)


class Command(BaseCommand):
    args = ''
    help = 'Mirrors all URLs associated with a state.'
    option_list = BaseCommand.option_list + (
        make_option('--loglevel',
                    action='store',
                    dest='loglevel',
                    default='info'),
        make_option('--output',
                    action='store',
                    dest='output',
                    default='-'),
    )

    def handle(self, *args, **options):
        log_handler = configure_log_handler('mirrorstate',
                                            options['loglevel'], options['output'])
        with logbook.NullHandler():
            with log_handler.applicationbound():

                local_timezone = pytz.timezone(settings.TIME_ZONE)
                now = pytz.datetime.datetime.now(tz=local_timezone)
               
                urls = list(ElectionUrl.objects.filter(state__in=args))
                def timestamp_or_none(urlobj):
                    mirror = urlobj.latest_mirror()
                    return mirror.timestamp if mirror else None
                urls.sort(key=timestamp_or_none)
               
                for url in urls:
                    previous = url.latest_mirror()
                    if previous:
                        # Don't mirror URLs too often
                        since_last = now - previous.timestamp
                        if since_last < settings.MIRROR_WAIT:
                            wait = math.floor((settings.MIRROR_WAIT - since_last).total_seconds())
                            log.notice("Waiting {0} seconds before mirroring again: {1}".format(
                                url.url, wait))
                            time.sleep(wait)

                    mirror_url(url)


