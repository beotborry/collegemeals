from django.db.models import Avg
from rest_framework import serializers
from .models import College, Restaurant, Meal, Review

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'meal', 'score')

class MealSerializer(serializers.ModelSerializer):
    score = serializers.SerializerMethodField()
    score_count = serializers.SerializerMethodField()
    class Meta:
        model = Meal
        fields = ('id', 'name', 'restaurant', 'score', 'score_count')
    def get_score(self, meal):
        return Review.objects.filter(meal=meal).aggregate(Avg('score'))
    def get_score_count(self, meal):
        return Review.objects.filter(meal=meal).count()

class RestaurantSerializer(serializers.ModelSerializer):
    meal = MealSerializer(many=True)
    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'meal')

class CollegeSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(many=True)
    class Meta:
        model = College
        field = ('id', 'name', 'restaurant')





