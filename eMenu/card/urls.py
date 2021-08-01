from django.urls import path
from card.views import CardListView, CardDetailView

urlpatterns = [
    path('', CardListView.as_view(), name='card-list'),
    path('<int:pk>/', CardDetailView.as_view(), name='card-detail')
]
