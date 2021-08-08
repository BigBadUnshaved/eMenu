from django.urls import path

from . import views, new_views


urlpatterns = [
    path('', new_views.CardListView.as_view(), name='card-ui-list'),
    path('<int:pk>/',
        new_views.CardRetrieveDestroyView.as_view(),
        name='card-ui-detail'
    ),
    path('new/', new_views.CardCreateView.as_view(), name='card-ui-create'),
    path('<int:pk>/edit/', new_views.CardUpdateView.as_view(), name='card-ui-edit'),
    path('dish', views.DishListView.as_view(), name='dish-ui-list'),
    path('dish/<int:pk>/', views.DishDetailView.as_view(), name='dish-ui-detail'),
    path('dish/new/', views.DishCreateView.as_view(), name='dish-ui-create'),
    path('dish/<int:pk>/edit/', views.DishUpdateView.as_view(), name='dish-ui-edit'),
    path(
        'dish/<int:pk>/delete/',
        views.DishDeleteView.as_view(),
        name='dish-ui-delete'
    ),
]
