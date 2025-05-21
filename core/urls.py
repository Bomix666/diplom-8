from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('schedule/', views.schedule, name='schedule'),
    path('grades/', views.grades, name='grades'),
    path('profile/', views.profile, name='profile'),
]
