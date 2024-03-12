from apps.game import views
from django.contrib import admin
from django.urls import path, include
import uuid

urlpatterns = [
    path('',views.index, name="index"),
    path('<uuid:room_id>/', views.waiting, name='waiting'),
]
