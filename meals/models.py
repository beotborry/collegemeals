from django.db import models
from django.utils import timezone

class College(models.Model):
    name = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name

class Restaurant(models.Model):
    name = models.TextField()
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name

class Meal(models.Model):
    name = models.TextField()
    price = models.TextField()
    TYPES = (('BR', 'breakfast'), ('LU', 'lunch'), ('DN', 'dinner'))
    type = models.CharField(max_length=2, choices=TYPES, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name


class Review(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    score = models.IntegerField()
    created = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.score

class RestaurantInformation(models.Model):
    type = models.TextField()
    body = models.TextField()
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    def __str__(self):
        return self.type

class Menu(models.Model):
    date = models.DateField()
    meals = models.ManyToManyField(Meal)
    restaurant = models.ForeignKey(Restaurant)
    def __str__(self):
        return "%s:%s" % (self.date, self.restaurant.name)