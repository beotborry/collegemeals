from django.core.management.base import BaseCommand, CommandError
from meals.models import College, Restaurant

COLLEGE_NAME = "yonsei"
KUKJE_RESTAURANTS = ["Y-플라자", "송도1학사", "송도2학사"]
STUDENT_RESTAURANTS = ["카페테리아(맛나샘)", "푸드코트(부를샘)"]
HANKYUNG_RESTAURANTS = ["한경관(교직원식당)"]

class Command(BaseCommand):
    help = 'Creates the neccessary university and restaurants for crawler'

    def handle(self, *args, **options):
        college, created = College.objects.get_or_create(name=COLLEGE_NAME)
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created "%s" university' % COLLEGE_NAME))
        else:
            self.stdout.write(self.style.WARNING('"%s" university already exists'))
        for name in KUKJE_RESTAURANTS + STUDENT_RESTAURANTS + HANKYUNG_RESTAURANTS:
            _, created = Restaurant.objects.get_or_create(name=name, college=college)
            if created:
                self.stdout.write(self.style.SUCCESS('Successfully created "%s" restaurant' % name))
