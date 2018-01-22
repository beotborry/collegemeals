from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, parser_classes
from rest_framework import generics, status
from rest_framework.response import Response

from meals.models import Menu, Restaurant
from meals.serializers import MenuSerializer

KUKJE_RESTAURANTS = ["Y-플라자", "송도1학사", "송도2학사"]
STUDENT_RESTAURANTS = ["카페테리아(맛나샘)", "푸드코트(부를샘)"]
HANKYUNG_RESTAURANTS = ["한경관(교직원식당)"]

@api_view(['GET'])
def menu(request):
    today = timezone.localtime(timezone.now()).date()
    tomorrow = (timezone.localtime(timezone.now()).today() + timedelta(days=1)).date()
    menu_data = { "today": { "date": today.__str__(), "menus": [] }, "tomorrow": { "date": tomorrow.__str__(), "menus": [] } }
    for restaurant_name in KUKJE_RESTAURANTS:
        restaurant = Restaurant.objects.get(name=restaurant_name)
        today_menu = Menu.objects.get(restaurant=restaurant, date=today)
        menu_data["today"]["menus"].append(MenuSerializer(today_menu).data)
        tomorrow_menu = Menu.objects.get(restaurant=restaurant, date=tomorrow)
        menu_data["tomorrow"]["menus"].append(MenuSerializer(tomorrow_menu).data)
    return Response(data=menu_data)
