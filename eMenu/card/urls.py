from django.urls import path
from card.views import CardListView, CardDetailView, CardCreateView

urlpatterns = [
    path('', CardListView.as_view(), name='card-list'),
    path('<int:pk>/', CardDetailView.as_view(), name='card-detail'),
    path('new/', CardCreateView.as_view(), name='card-create'),
]
