import requests
from bs4 import BeautifulSoup
import re

from django.utils import timezone
from meals.models import Meal, Menu, Restaurant

from .settings import GRADUATE_DORM_RESTAURANTS, SNUCO_RESTAURANTS, VET_RESTAURANTS

def crawl():
    crawl_graduate_restaurant()
    crawl_snuco_restaurants()
    crawl_vet_restaurant()

def dates_handler(dates, restaurant_name):
    restaurant = Restaurant.objects.get(name=restaurant_name)
    for date in dates:
        Menu.objects.get_or_create(date=date, restaurant=restaurant)

def crawl_graduate_dorm_restaurant():
    # TODO
    '''
    1. Use dates_handler to create Menu objects
    2. Get or create each Meal object
       A Meal must have a name(string), type(char(2)"BR"|"LU"|"DN") , restaurant(foreign key) and price(string).
    3. Add each meal to the Menu object it belongs in. ([ex]menu.meals.add(meal))
    '''
    pass

def crawl_snuco_restaurants():
    # TODO
    '''
    1. Use dates_handler to create Menu objects
    2. Get or create each Meal object
       A Meal must have a name(string), type(char(2)"BR"|"LU"|"DN") , restaurant(foreign key) and price(string).
    3. Add each meal to the Menu object it belongs in. ([ex]menu.meals.add(meal))
    '''
    pass

def crawl_vet_restaurant():
    # TODO
    '''
    1. Use dates_handler to create Menu objects
    2. Get or create each Meal object
       A Meal must have a name(string), type(char(2)"BR"|"LU"|"DN") , restaurant(foreign key) and price("Etc").
    3. Add each meal to the Menu object it belongs in. ([ex]menu.meals.add(meal))
    '''
    pass
