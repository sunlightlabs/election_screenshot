from django.core.management.base import NoArgsCommand
from screenshotter.models import ElectionUrl


class Command(NoArgsCommand):
    args = ''
    help = 'Prints a list of all states in the database.'

    def handle(self, *args, **options):
        state_groups = sorted(list(ElectionUrl.objects.values('state').distinct()))
        for group in state_groups:
            print group['state']


