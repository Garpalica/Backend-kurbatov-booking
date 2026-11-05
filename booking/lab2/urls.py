from django.urls import path
from django.contrib import admin
from lab2 import views

urlpatterns = [
    path('api/rooms/', views.rooms),
    path('api/rooms/<int:id>', views.rooms),
    path('health/', views.health)
]
