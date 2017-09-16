from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^menu/college/(?P<college_id>[0-9]+)/$', views.menu),
    url(r'^review/college/(?P<college_id>[0-9]+)/meal/(?P<meal_id>[0-9]+)/$', views.review),
]