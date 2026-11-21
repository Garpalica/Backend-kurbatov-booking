from django.urls import path
from django.contrib import admin
from lab4 import views

urlpatterns = [
    path('', views.index, name='home'),
]
