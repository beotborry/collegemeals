from django.core.management.base import BaseCommand, CommandError
from snu.crawler import crawl

class Command(BaseCommand):
    help = 'snu crawler, must be run at least once a week on sundays'

    def handle(self, *args, **options):
        crawl()