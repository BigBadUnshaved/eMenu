from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
    path('cards/', views.CardAPIList.as_view()),
    path('cards/<int:pk>/', views.CardAPIDetail.as_view()),
    path('dishes/', views.DishAPIList.as_view()),
    path('dishes/<int:pk>/', views.DishAPIDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
