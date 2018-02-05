import requests
from bs4 import BeautifulSoup
import re

from django.utils import timezone
from meals.models import Meal, Menu, Restaurant

from .settings import GRADUATE_DORM_RESTAURANTS, SNUCO_RESTAURANTS, VET_RESTAURANTS

def vet_get_date(date):
    year = timezone.localtime(timezone.now()).year
    month = re.compile('([0-9]{0,2})').findall(date)[0]
    day = re.compile('([0-9]{0,2})').findall(date)[3]
    return '%s-%s-%s' % (year, month, day)

def crawl():
    crawl_vet_restaurant()

def dates_handler(date, restaurant_name):
    restaurant = Restaurant.objects.get(name = restaurant_name)
    Menu.objects.get_or_create(date = date, restaurant = restaurant)


def vet_meal_handler(type, meal_name, price, date, restaurant_name):
    restaurant = Restaurant.objects.get(name = restaurant_name)

    menu = Menu.objects.get(date = date, restaurant = restaurant)
    meal, _ = Meal.objects.get_or_create(name = meal_name, type = type, price = price, restaurant = restaurant)
    meal.save()
    menu.meals.add(meal)

def crawl_vet_restaurant():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'}

    page = requests.get('http://vet.snu.ac.kr/node/152', headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    soup.div.extract()
    tds = soup.find_all('td')
    current_restaurant = '수의대식당'
    count = 0

    for td in tds:

        content = td.text
        type_handler = {'중식': 'LU', '석식': 'DN'}

        if count == 0:
            date = vet_get_date(content)
            dates_handler(date = date, restaurant_name=current_restaurant)
            count += 1
            continue
        elif count == 1:
            lunch = content
            if lunch == " " or lunch == '\t' or lunch is None:
                count += 1
                continue
            vet_meal_handler(type = type_handler['중식'], meal_name = lunch, price = 'etc', date = date, restaurant_name = current_restaurant)
            count += 1
            continue
        elif count == 2:
            dinner = content
            if dinner == " " or dinner == '\t' or dinner is None:
                count += 1
                continue
            vet_meal_handler(type = type_handler['석식'], meal_name = dinner, price = 'etc', date = date, restaurant_name = current_restaurant)
            count = 0
            continue
