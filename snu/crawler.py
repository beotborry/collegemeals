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

def graduate_dorm_get_date(date):
    year = timezone.localtime(timezone.now()).year
    month = re.compile('([0-9]{0,2})').findall(date)[2]
    day = re.compile('([0-9]{0,2})').findall(date)[4]
    return '%s-%s-%s' % (year, month, day)

def crawl():
    crawl_graduate_dorm_restaurant()
    crawl_vet_restaurant()

def dates_handler(date, restaurant_name):
    restaurant = Restaurant.objects.get(name = restaurant_name)
    Menu.objects.get_or_create(date = date, restaurant = restaurant)


def meal_handler(type, meal_name, price, date, restaurant_name):
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
            meal_handler(type = type_handler['중식'], meal_name = lunch, price = 'etc', date = date, restaurant_name = current_restaurant)
            count += 1
            continue
        elif count == 2:
            dinner = content
            if dinner == " " or dinner == '\t' or dinner is None:
                count += 1
                continue
            meal_handler(type = type_handler['석식'], meal_name = dinner, price = 'etc', date = date, restaurant_name = current_restaurant)
            count = 0
            continue

def crawl_graduate_dorm_restaurant():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'}

    page = requests.get('http://dorm.snu.ac.kr/dk_board/facility/food.php', headers = headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    soup.div.extract()
    current_restaurant = '대학원기숙사식당'
    type_handler = { 1 : 'BR', 2 : 'LU', 3 : 'DN'}
    price_handler = {'menu_a' : 2000, 'menu_b' : 2500, 'menu_c' : 3000, 'menu_d' : 3500, 'menu_e' : 4000, 'menu_f' : 5000, '' : 0}

    column_count = 0
    row_count = 0
    trs = soup.select('table > tbody > tr')

    #0번째는 구분, 1번째 부터 날짜 list처럼 사용
    ths = soup.select('table > thead > tr > th')

    for th in ths:
        if th.attrs.get('colspan') == '3':
            continue
        date = graduate_dorm_get_date(th.text)
        dates_handler(date= date, restaurant_name=current_restaurant)

    def type_determine(row_count):
        if row_count == 0 or row_count == 1:
            return 1
        elif row_count == 2 or row_count == 3 or row_count == 4:
            return 2
        elif row_count == 5 or row_count == 6 or row_count == 7:
            return 3

    # date만 해결하면 됨
    for tr in trs:
        for td in trs[row_count].find_all('td'):
            if not td.li:
                continue
            column_count += 1
            meal_handler(type=type_handler[type_determine(row_count=row_count)], meal_name=td.text, price=price_handler[td.li.attrs['class'][0]], date=graduate_dorm_get_date(ths[column_count].text), restaurant_name= current_restaurant)

        row_count += 1
        column_count = 0

        if row_count == 8:
            break
