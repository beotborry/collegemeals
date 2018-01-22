from django.core.management.base import BaseCommand, CommandError
from meals.models import College, Restaurant
from snu.settings import COLLEGE_NAME, RESTAURANTS

class Command(BaseCommand):
    help = 'Creates the neccessary university and restaurants for crawler'

    def handle(self, *args, **options):
        college, created = College.objects.get_or_create(name=COLLEGE_NAME)
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created "%s" university' % COLLEGE_NAME))
        else:
            self.stdout.write(self.style.WARNING('"%s" university already exists'))
        for name in RESTAURANTS:
            _, created = Restaurant.objects.get_or_create(name=name, college=college)
            if created:
                self.stdout.write(self.style.SUCCESS('Successfully created "%s" restaurant' % name))
