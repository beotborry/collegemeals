from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, parser_classes
from rest_framework import generics, status
from rest_framework.response import Response
from .settings import RESTAURANTS
from meals.models import Restaurant, Menu
from meals.serializers import MenuSerializer

@api_view(['GET'])
def menu(request):
    today = timezone.localtime(timezone.now()).date()
    tomorrow = (timezone.localtime(timezone.now()).today() + timedelta(days=1)).date()
    menu_data = { "today": { "date": today.__str__(), "menus": [] }, "tomorrow": { "date": tomorrow.__str__(), "menus": [] } }
    for restaurant_name in RESTAURANTS:
        restaurant = Restaurant.objects.get(name=restaurant_name)
        today_menu = Menu.objects.get(restaurant=restaurant, date=today)
        menu_data["today"]["menus"].append(MenuSerializer(today_menu).data)
        tomorrow_menu = Menu.objects.get(restaurant=restaurant, date=tomorrow)
        menu_data["tomorrow"]["menus"].append(MenuSerializer(tomorrow_menu).data)
    return Response(data=menu_data)

@api_view(['POST'])
def review(request, meal_id):
    score = request.data.get('score')
    if not score:
        return Response(data={'message': 'Missing "score" field.'}, status=status.HTTP_400_BAD_REQUEST)
    Review.objects.create(meal_id=meal_id, score=score)
    return Response(data={'message': 'Review successful'})
