from django.urls import path
from card.views import CardListView

urlpatterns = [
    path('card/', CardListView.as_view(), name='card-list'),
]
