import os
import math
import time
from operator import itemgetter
import logbook
import pytz
from optparse import make_option
from django.db.models import Max
from django.core.management.base import BaseCommand
from screenshotter.models import ElectionUrl, ElectionMirror
from screenshotter.wget import mirror_url
from utils import configure_log_handler, restart_process
from django.conf import settings


_script_ = (os.path.basename(__file__)
            if __name__ == "__main__"
            else __name__)
log = logbook.Logger(_script_)


class Command(BaseCommand):
    args = ''
    help = 'Takes screenshots of all of the urls.'
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
        log_handler = configure_log_handler('mirrormirror',
                                            options['loglevel'], options['output'])
        with logbook.NullHandler():
            with log_handler.applicationbound():

                local_timezone = pytz.timezone(settings.TIME_ZONE)
                now = pytz.datetime.datetime.now(tz=local_timezone)
               
                if ElectionMirror.objects.count() == 0:
                    urls = ElectionUrl.objects.all()
                else:
                    # URLs that have never been mirrored
                    urls = ElectionUrl.objects.filter(mirrors__isnull=True)[:settings.MIRROR_BATCH_SIZE]
                    if not urls:
                        mirror_timestamps = list(ElectionMirror.objects
                                                 .values('election_url')
                                                 .annotate(timestamp=Max('timestamp')))
                        mirror_timestamps.sort(key=itemgetter('timestamp'))
                        batch_urls = [m['election_url'] for m in mirror_timestamps][:settings.MIRROR_BATCH_SIZE]
                        urls = ElectionUrl.objects.filter(pk__in=batch_urls)
               
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

                restart_process()


