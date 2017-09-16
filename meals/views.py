from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.decorators import api_view, parser_classes
from rest_framework import generics, status
from rest_framework.response import Response

from .models import College, Restaurant, Meal, Review
from .serializers import CollegeSerializer, RestaurantSerializer, MealSerializer, ReviewSerializer

@api_view(['GET'])
def menu(request, college_id):
    college = College.objects.get(pk=college_id)
    return Response(CollegeSerializer(college).data)

@api_view(['POST'])
def review(request, college_id, meal_id):
    college = College.objects.get(pk=college_id)
    score = request.data.get('score', '')
    if not score:
        return Response(data={'message': 'Missing fields.'}, status=status.HTTP_400_BAD_REQUEST)
    Review.objects.create(meal_id=meal_id, score=score)
    return Response(CollegeSerializer(college).data)