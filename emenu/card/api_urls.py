from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
    path('cards/', views.CardAPIList.as_view(), name='card-list'),
    path('cards_nice/', views.CardAPITemplateList.as_view(), name='card-nice-list'),
    path('cards/<int:pk>/', views.CardAPIDetail.as_view(), name='card-detail'),
    path('dishes/', views.DishAPIList.as_view(), name='dish-detail'),
    path('dishes/<int:pk>/', views.DishAPIDetail.as_view(), name='dish-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
