from django.urls import path
from . import views

urlpatterns = [
    path('', views.CardListView.as_view(), name='card-list'),
    path('<int:pk>/', views.CardDetailView.as_view(), name='card-detail'),
    path('new/', views.CardCreateView.as_view(), name='card-create'),
    path('<int:pk>/edit/', views.CardUpdateView.as_view(), name='card-edit'),
    path('<int:pk>/delete/', views.CardDeleteView.as_view(),
        name='card-delete'
    ),
    path('dish', views.DishListView.as_view(), name='dish-list'),
]
