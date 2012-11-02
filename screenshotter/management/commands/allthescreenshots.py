import logbook
from optparse import make_option
from django.core.management.base import BaseCommand
from screenshotter.models import ElectionUrl
from screenshotter.phantomjs import ensure_phantomjs_is_runnable
from utils import configure_log_handler

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
        ensure_phantomjs_is_runnable()
        log_handler = configure_log_handler('allthescreenshots',
                                            options['loglevel'], options['output'])
        with logbook.NullHandler():
            with log_handler.applicationbound():
                for url in ElectionUrl.objects.all():
                    url.take_screenshot()
