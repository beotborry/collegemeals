from django.core.management.base import BaseCommand, CommandError
from yonsei.crawler import crawl

class Command(BaseCommand):
    help = 'yonsei crawler, must be run at least once a week on sundays'

    def handle(self, *args, **options):
        crawl()