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
    crawl_snuco_direct_restaurant()
    crawl_snuco_commission_restaurant()

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

        if count == 0:
            date = vet_get_date(content)
            dates_handler(date = date, restaurant_name=current_restaurant)
            count += 1
            continue
        elif count == 1:
            lunch = content
            if lunch == ' ':
                count += 1
                continue
            meal_handler(type = 'LU', meal_name = lunch, price = 'etc', date = date, restaurant_name = current_restaurant)
            count += 1
            continue
        elif count == 2:
            dinner = content
            if dinner == ' ':
                count = 0
                continue
            meal_handler(type = 'DN', meal_name = dinner, price = 'etc', date = date, restaurant_name = current_restaurant)
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

    for tr in trs:
        for td in trs[row_count].find_all('td'):
            if not td.li:
                continue
            column_count += 1
            meal_handler(type=type_handler[type_determine(row_count=row_count)], meal_name=td.text.replace('\n',''), price=price_handler[td.li.attrs['class'][0]], date=graduate_dorm_get_date(ths[column_count].text), restaurant_name= current_restaurant)

        row_count += 1
        column_count = 0

        if row_count == 8:
            break

def crawl_snuco_direct_restaurant():

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'}

    url_origin = 'http://www.snuco.com/html/restaurant/restaurant_menu1.asp'
    url_date = ''

    page = requests.get(url= url_origin, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    soup.div.extract()

    current_restaurant = ''
    restaurant_handler = {1: '학생회관 식당', 2: '농생대 3식당', 3: '919동 기숙사 식당', 4: '자하연 식당', 5: '302동 식당', 6: '동원관 식당'}
    price_handler = {'ⓐ' : 2500, 'ⓑ' : 3000, 'ⓒ': 3500, 'ⓓ': 4000, 'ⓔ': 4500, 'ⓕ': 5000, 'ⓖ': 'etc', 'ⓙ' : 6000}

    a_tags = soup.find_all('a')
    trs = soup.find_all('tr')
    tr_count = 0

    for tr in trs:
        tr_count += 1
        if tr_count >= 20 and tr_count <= 25:
            current_restaurant = restaurant_handler[tr_count - 19]

            for a in [tag for tag in a_tags if (tag.attrs['href'] and tag.attrs['href'][0] == '?')]:
                date = a.attrs['href'][6:16]
                dates_handler(date=date, restaurant_name=current_restaurant)
                url_date = url_origin + str('?date=') + str(date)

                page_date = requests.get(url=url_date, headers=headers)
                soup_date = BeautifulSoup(page_date.content, 'html.parser')
                soup_date.div.extract()

                tr_date_count = 0
                trs_date = soup_date.find_all('tr')
                for tr_date in trs_date:
                    tr_date_count += 1
                    if tr_date_count == tr_count + 1:
                        tds_date = tr_date.find_all('td')

                        first_br = re.split('.(?=[ⓐ-ⓙ])', tds_date[2].text.replace('\n', ''))
                        second_br = re.compile('.(?=[ⓐ-ⓙ])').findall(tds_date[2].text.replace('\n', ''))
                        second_br.append('')
                        third_br = [first_br[i] + second_br[i].replace('/','') for i in range(len(first_br))]

                        for menu in third_br:
                            if not menu == ' ':
                                meal_handler(type='BR', meal_name=menu[1:].replace(' ',''), price=price_handler[menu[0]], date=date, restaurant_name=current_restaurant)

                        first_lu = re.split('.(?=[ⓐ-ⓙ])', tds_date[4].text.replace('\n', ''))
                        second_lu = re.compile('.(?=[ⓐ-ⓙ])').findall(tds_date[4].text.replace('\n', ''))
                        second_lu.append('')
                        third_lu = [first_lu[i] + second_lu[i].replace('/','') for i in range(len(first_lu))]

                        for menu in third_lu:
                            if not menu == ' ':
                                meal_handler(type='LU', meal_name=menu[1:].replace(' ',''), price=price_handler[menu[0]], date=date, restaurant_name=current_restaurant)

                        first_dn = re.split('.(?=[ⓐ-ⓙ])', tds_date[6].text.replace('\n', ''))
                        second_dn = re.compile('.(?=[ⓐ-ⓙ])').findall(tds_date[6].text.replace('\n', ''))
                        second_dn.append('')
                        third_dn = [first_dn[i] + second_dn[i].replace('/', '') for i in range(len(first_dn))]

                        for menu in third_dn:
                            if not menu == ' ':
                                meal_handler(type='DN', meal_name=menu[1:].replace(' ',''), price=price_handler[menu[0]], date=date, restaurant_name=current_restaurant)

def crawl_snuco_commission_restaurant():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'}

    url_origin = 'http://www.snuco.com/html/restaurant/restaurant_menu2.asp'
    url_date = ''

    page = requests.get(url=url_origin, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    soup.div.extract()

    current_restaurant = ''
    restaurant_handler = {1: '사범대 4식당', 2: '두레미담', 3: '301동 식당', 4: '예술계복합연구동 식당', 5: '샤반', 6: '공대간이식당', 7: '소담마루', 8: '220동 식당', 10: '감골 식당'}
    price_handler = {'ⓐ': 1700, 'ⓑ': 2000, 'ⓒ': 2500, 'ⓓ': 3000, 'ⓔ': 3500, 'ⓕ': 4000, 'ⓖ': 4500, 'ⓗ' : 5000, 'ⓘ' : 5500, 'ⓙ': 6000, 'ⓚ' : 6500}

    a_tags = soup.find_all('a')
    trs = soup.find_all('tr')
    tr_count = 0

    table_first_row = 21
    table_last_row = 30
    for tr in trs:
        tr_count += 1
        if tr_count >= table_first_row and tr_count <= table_last_row:
            if tr_count == 29: #라운지오 넘김
                continue
            current_restaurant = restaurant_handler[tr_count - 20]

            for a in [tag for tag in a_tags if (tag.attrs['href'] and tag.attrs['href'][0] == '?')]:
                date = a.attrs['href'][6:16]
                dates_handler(date=date, restaurant_name=current_restaurant)
                url_date = url_origin + str('?date=') + str(date)

                page_date = requests.get(url=url_date, headers=headers)
                soup_date = BeautifulSoup(page_date.content, 'html.parser')
                soup_date.div.extract()

                tr_date_count = 0
                trs_date = soup_date.find_all('tr')
                for tr_date in trs_date:
                    tr_date_count += 1
                    if tr_date_count == tr_count:
                        tds_date = tr_date.find_all('td')

                        first_br = re.split('.(?=[ⓐ-ⓚ])', tds_date[2].text.replace('\n', ''))
                        second_br = re.compile('.(?=[ⓐ-ⓚ])').findall(tds_date[2].text.replace('\n', ''))
                        second_br.append('')
                        third_br = [first_br[i] + second_br[i].replace('/','') for i in range(len(first_br))]

                        for menu in third_br:
                            if not menu == ' ':
                                if menu[0] in price_handler.keys():
                                    meal_handler(type='BR', meal_name=menu[1:].replace(' ',''), price=price_handler[menu[0]], date=date, restaurant_name=current_restaurant)
                                else:
                                    meal_handler(type='BR', meal_name=menu.replace(' ',''), price='etc', date=date, restaurant_name=current_restaurant)

                        if tr_count == 26:
                            prices = re.findall('<\d+>', tds_date[4].text.replace('\n',''))
                            menu = re.split('<\d+>', tds_date[4].text.replace('\n',''))
                            for index, price in enumerate(prices):
                                meal_handler(type='LU', meal_name=menu[index + 1], price=price.replace('<','').replace('>',''), date= date, restaurant_name=current_restaurant)
                        else:
                            first_lu = re.split('.(?=[ⓐ-ⓚ])', tds_date[4].text.replace('\n', ''))
                            second_lu = re.compile('.(?=[ⓐ-ⓚ])').findall(tds_date[4].text.replace('\n', ''))
                            second_lu.append('')
                            third_lu = [first_lu[i] + second_lu[i].replace('/','') for i in range(len(first_lu))]

                            for menu in third_lu:
                                if not menu == ' ':
                                    if menu[0] in price_handler.keys():
                                        meal_handler(type='LU', meal_name=menu[1:].replace(' ',''), price=price_handler[menu[0]], date=date, restaurant_name=current_restaurant)
                                    else:
                                        meal_handler(type='LU', meal_name=menu.replace(' ',''), price='etc', date=date, restaurant_name=current_restaurant)

                        if tr_count == 26:
                            prices  = re.findall('<\d+>', tds_date[6].text.replace('\n',''))
                            menu = re.split('<\d+>', tds_date[6].text.replace('\n',''))
                            for index, price in enumerate(prices):
                                meal_handler(type='DN', meal_name=menu[index + 1], price=price.replace('<','').replace('>',''), date=date, restaurant_name=current_restaurant)
                        else:
                            first_dn = re.split('.(?=[ⓐ-ⓚ])', tds_date[6].text.replace('\n', ''))
                            second_dn = re.compile('.(?=[ⓐ-ⓚ])').findall(tds_date[6].text.replace('\n', ''))
                            second_dn.append('')
                            third_dn = [first_dn[i] + second_dn[i].replace('/', '') for i in range(len(first_dn))]

                            for menu in third_dn:
                                if not menu == ' ':
                                    if menu[0] in price_handler.keys():
                                        meal_handler(type='DN', meal_name=menu[1:].replace(' ',''), price=price_handler[menu[0]], date=date, restaurant_name=current_restaurant)
                                    else:
                                        meal_handler(type='DN', meal_name=menu.replace(' ',''), price='etc', date=date, restaurant_name=current_restaurant)

