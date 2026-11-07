from django.urls import path
from django.contrib import admin
from lab1 import views

urlpatterns = [
    path('', views.home),
    path('api/rooms/', views.rooms),
    path('api/rooms/<int:id>', views.rooms),
    # path('api/rooms/<int:room_id>/bookings/', views.bookings),
    path('health/', views.health)
]
