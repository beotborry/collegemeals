import requests
from bs4 import BeautifulSoup
import re

from django.utils import timezone
from meals.models import Meal, Menu, Restaurant

def crawl():
    kukje_crawler()
    student_crawler()
    hankyung_crawler()

def dates_handler(dates, restaurant_name):
    restaurant = Restaurant.objects.get(name=restaurant_name)
    for date in dates:
        Menu.objects.get_or_create(date=date, restaurant=restaurant)

def meal_handler(type, meals, prices, dates, restaurant_name):
    restaurant = Restaurant.objects.get(name=restaurant_name)
    for index, meal_names in enumerate(meals):
        is_here = False
        if not meal_names:
            continue
        if isinstance(meal_names, list):
            for meal_name in meal_names:
                meal, _ = Meal.objects.get_or_create(name=meal_name, type=type, restaurant=restaurant)
                meal.price = prices[index]
                meal.save()
                menu = Menu.objects.get(date=dates[index], restaurant=restaurant)
                menu.meals.add(meal)
        else:
            meal, _ = Meal.objects.get_or_create(name=meal_names, type=type, restaurant=restaurant)
            meal.price = prices[index]
            meal.save()
            menu = Menu.objects.get(date=dates[index], restaurant=restaurant)
            menu.meals.add(meal)

def kukje_crawler():
    page = requests.get('http://coop.yonsei.ac.kr/Menu/Kukje.asp')
    soup = BeautifulSoup(page.content, 'html.parser')
    KUKJE_RESTAURANTS = ["Y-플라자", "송도1학사", "송도2학사"]
    KUKJE_DIVISIONS = [["Soban", "Western 1", "Western 2", "Chef's special", "Hotbowl 1", "Hotbowl 2", "Chinese 1", "Chinese 2"], ["Hot Bowl", "Western", "HotBowl", "Westernl", "Snack"], ["Korean", "International", "컵밥"]]
    KUKJE_MEAL_TIMES = ["(아침)", "(점심)", "(저녁)"]
    COLUMN_COUNT = 8
    division_time_mixed_re = re.compile("(.*)(\(아침\)|\(점심\)|\(저녁\))")
    chinese2_meal_re = re.compile("[-,0-9]{,}00원")
    dates = None
    meals = []
    prices = []
    current_meal_time = None
    current_division = None
    current_rowspan = 0
    current_row = 0
    current_col = 0
    for index, current_restaurant in enumerate(KUKJE_RESTAURANTS):
        sub_soup = soup.find("tr", id="lay%s" % (index)).table.table
        trs = sub_soup.table.find_all("tr") if sub_soup.table else sub_soup.find_all("tr")
        for tr in trs:
            if tr.td.attrs.get("colspan") == COLUMN_COUNT.__str__():
                tr.extract()
                continue
            current_rowspan = tr.td.attrs.get("rowspan", 1) if current_row == 0 else current_rowspan
            # Restaurant name and the dates 
            if tr.td.font and tr.td.font.attrs.get("color") == "#CCFF00":
                dates = [td.font.get_text().replace("\xa0", "") for td in tr.find_all("td")[1:]]
                def get_date(date):
                    year = timezone.localtime(timezone.now()).year
                    month = re.compile("([0-9]{0,2})월").findall(date)[0].zfill(2)
                    day = re.compile("([0-9]{0,2})일").findall(date)[0].zfill(2)
                    return "%s-%s-%s" % (year, month, day)
                dates = list(map(get_date, dates))
                dates_handler(dates=dates, restaurant_name=current_restaurant)
                continue
            if current_row == 0:
                current_rowspan = int(tr.td.attrs.get("rowspan", 1))
                td = tr.td
                current_division = ""
                current_meal_time = ""
                for font in [ele.get_text() for ele in td.find_all("font")]:
                    if KUKJE_DIVISIONS[index].__contains__(font):
                        current_division = font
                    elif KUKJE_MEAL_TIMES.__contains__(font):
                        current_meal_time = font
                    mixed_datum = division_time_mixed_re.findall(font)
                    if mixed_datum and mixed_datum[0] and mixed_datum[0][0] and mixed_datum[0][1]:
                        current_division = mixed_datum[0][0]
                        current_meal_time = mixed_datum[0][1]
            if (current_rowspan == 2 and current_row == 0) or (current_rowspan == 3 and current_row == 1):
                for td in tr.find_all("td"):
                    meal = td.font.get_text() if td.font else td.get_text().replace("\n", "").replace("\r", "").replace("\xa0", "").strip()
                    colspan = int(td.attrs.get("colspan", 1))
                    if td.attrs.get("rowspan") == "2" and chinese2_meal_re.search(meal):
                        price = []
                        tokens = chinese2_meal_re.findall(meal)
                        price = tokens[0]
                        meal_split = meal.split(price)
                        meal = "%s(%s)" % (meal_split[0].replace('-', '').strip(), meal_split[1].replace('-', ''))
                        prices += colspan * [price]
                    meals += colspan * [meal]
                if current_rowspan == 2 and current_row == 0:
                    meals.__delitem__(0)
                meals = list(filter(("").__ne__, meals))
            if (current_rowspan == 2 and current_row == 1) or (current_rowspan == 3 and current_row == 2):
                for td in tr.find_all("td"):
                    price = td.font.get_text() if td.font else td.get_text().replace("\n", "").replace("\r", "").replace("\xa0", "").strip()
                    colspan = int(td.attrs.get("colspan", 1))
                    prices += colspan * [price]
                    prices = list(filter(("").__ne__, prices))
                while prices.__len__() < meals.__len__():
                    meals.pop()
                type_handler = {"(아침)": "BR", "(점심)": "LU", "(저녁)": "DN"}
                type = type_handler.get(current_meal_time, "")
                meal_handler(type=type, meals=meals, prices=prices, dates=dates, restaurant_name=current_restaurant)
                meals = []
                prices = []
            current_row += 1
            if current_row == current_rowspan:
                current_row = 0

def student_crawler():
    page = requests.get("https://coop.yonsei.ac.kr:5013/Menu/Student.asp")
    soup = BeautifulSoup(page.content, "html.parser")
    soup.table.tr.extract()
    COLUMN_COUNT = 7
    dates = None
    meals = []
    prices = []
    current_restaurant = ""
    trs = soup.find_all("tr")
    isCafeteria = False
    current_rowspan = 2
    current_row = 0
    is_first_row = True
    meal_price_re = re.compile("(.*)/(.*)")
    chinese_meal_type1_re = re.compile("(.*)/단품(.*),곱배기(.*)")
    chinese_meal_type2_re = re.compile("(.*)/단품(.*) 곱배기 (.*)")

    for tr in trs:
        if tr.td.attrs.get("colspan") == COLUMN_COUNT.__str__() or tr.td.attrs.get("colspan") == (COLUMN_COUNT - 1).__str__():
            tr.extract()
            continue
        if tr.td.font and tr.td.font.attrs.get("color") == "#CCFF00":
            current_restaurant = tr.td.font.get_text().replace("\r", "").replace("\n", "").replace(" ","")
            isCafeteria = not isCafeteria
            dates = [td.font.get_text() for td in tr.find_all("td")[1:COLUMN_COUNT]]
            def get_date(date):
                year = timezone.localtime(timezone.now()).year
                month = re.compile("([0-9]{0,2})/").findall(date)[0].zfill(2)
                day = re.compile("/([0-9]{0,2})").findall(date)[0].zfill(2)
                return "%s-%s-%s" % (year, month, day)
            dates = list(map(get_date, dates))
            dates_handler(dates=dates, restaurant_name=current_restaurant)
            continue
        if isCafeteria:
            if current_row == 0:
                meals = [ele.font.get_text() for ele in tr.find_all("td")]
                meals = meals[1:]
            elif current_row == 1:
                prices = [ele.get_text().replace("\r", "").replace("\n", "").replace(" ","") for ele in tr.find_all("td")]
                prices = prices[1:]
                type = "BR" if is_first_row else ""
                is_first_row = False
                meal_handler(type=type, meals = meals, prices=prices, dates=dates, restaurant_name=current_restaurant)
                meals = []
                prices = []
            current_row += 1
            if current_row == current_rowspan:
                current_row = 0
        else:
            for td in tr.find_all("td"):
                meal_price_text = td.get_text().replace("\r", "").replace("\n", "").strip()
                meal_price = None
                is_chinese = False
                if chinese_meal_type1_re.search(meal_price_text):
                    meal_price = chinese_meal_type1_re.findall(meal_price_text)[0]
                    is_chinese = True
                elif chinese_meal_type2_re.search(meal_price_text):
                    meal_price = chinese_meal_type2_re.findall(meal_price_text)[0]
                    is_chinese = True
                if is_chinese:
                    meals.append(["%s(단품)" % meal_price[0], "%s(곱배기)" % meal_price[0]])
                    prices.append([meal_price[1], meal_price[2]])
                elif meal_price_re.search(meal_price_text):
                    meal_price = meal_price_re.findall(meal_price_text)[0]
                    meals.append(meal_price[0])
                    prices.append(meal_price[1])
            if meals and prices:
                meal_handler(type="", meals = meals, prices=prices, dates=dates, restaurant_name=current_restaurant)
            meals = []
            prices = []

def hankyung_crawler():
    page = requests.get("https://coop.yonsei.ac.kr:5013/Menu/Hankyung.asp")
    soup = BeautifulSoup(page.content, "html.parser")
    soup.div.extract()
    COLUMN_COUNT = 7
    trs = soup.find_all("tr")
    dates = None
    current_restaurant = "한경관(교직원식당)"
    current_meal_time = ""
    current_floor = ""
    price_re = re.compile("[,0-9]{,}원")
    meals = [[] for _ in range(COLUMN_COUNT)]
    prices = []
    for tr in trs:
        if tr.td.attrs.get("bgcolor") == "#99CCCC":
            current_meal_time = tr.td.font.get_text().replace("\r", "").replace("\n", "").replace("\t", "").replace(" ", "")
            continue
        if int(tr.td.attrs.get("colspan", 1)) > 1:
            tr.extract()
            continue
        if tr.td.attrs.get("bgcolor") == "#1D8992":
            dates = [ele.font.get_text() for ele in tr.find_all("td")][1:]
            def get_date(date):
                year = timezone.localtime(timezone.now()).year
                month = re.compile("([0-9]{0,2})/").findall(date)[0].zfill(2)
                day = re.compile("/([0-9]{0,2})").findall(date)[0].zfill(2)
                return "%s-%s-%s" % (year, month, day)
            dates = list(map(get_date, dates))
            dates_handler(dates=dates, restaurant_name=current_restaurant)
            continue
        if tr.td.b:
            current_floor == tr.td.b.get_text()
        if price_re.search(tr.find_all("td")[1].font.get_text()):
            prices = [ele.font.get_text() for ele in tr.find_all("td")]
            meals = meals[1:]
            type_handler = {"중식": "LU", "석식": "DN"}
            meal_handler(type=type_handler[current_meal_time], meals = meals, prices=prices, dates=dates, restaurant_name=current_restaurant)
            meals = [[] for _ in range(COLUMN_COUNT)]
            prices = []
            
        else:
            for index, td in enumerate(tr.find_all("td")):
                if td.font.get_text().replace('\xa0', ''):
                    meals[index].append(td.font.get_text())