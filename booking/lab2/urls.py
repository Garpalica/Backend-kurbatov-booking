from django.urls import path
from django.contrib import admin
from lab2 import views

urlpatterns = [
    path('api/rooms/', views.rooms),
    path('api/rooms/<int:id>', views.rooms),
    path('api/rooms/<int:room_id>/bookings/', views.bookings),
    path('health/', views.health),
    path('api/rooms/stats/', views.stats)
]
