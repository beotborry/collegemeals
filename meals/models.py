from django.db import models
from django.utils import timezone

class College(models.Model):
    name = models.TextField()
    created = models.DateTimeField(default=timezone.now)

class Restaurant(models.Model):
    name = models.TextField()
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

class Meal(models.Model):
    name = models.TextField()
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

class Review(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    score = models.IntegerField()
    created = models.DateTimeField(default=timezone.now)