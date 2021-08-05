from django.db.models import Count

from django_filters import rest_framework as filters
from rest_framework import generics, permissions
from rest_framework.filters import OrderingFilter

from card.serializers import CardSerializer, DishSerializer
from card.models import Card, Dish


class EmenuCardAPIMixin():
    '''
    Custom mixin for django-rest Card views that contains shared data
    '''
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        '''
        We specify queryset by get_queryset and not attribute 
        because if user is not authenticated we have to exclude
        cards with no dishes
        '''
        queryset = Card.objects.all()\
                .prefetch_related('dishes')\
                .annotate(dishes_count=Count('dishes'))
        if not self.request.user.is_authenticated:
            queryset = Card.objects.exclude(dishes__isnull=True)
        return queryset


class CardAPIListFilterSet(filters.FilterSet):
    '''
    Filterset for CardList that included DateTimeToRangeFilter 
    for both Card.creation_date and Card.last_change_date
    '''
    creation_date = filters.DateTimeFromToRangeFilter()
    last_change_date = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Card
        fields = ['name', 'creation_date', 'last_change_date']


class CardAPIList(EmenuCardAPIMixin, generics.ListCreateAPIView):
    '''
    Create new card or list all menu cards using django rest api view;
    accepts following get parameters:
    'name' - equal to Card.objects.filter(name=value)
    'creation_date_after' - Card.objects.filter(creation_date__gte=value)
    'creation_date_before' - Card.objects.filter(creation_date__gte=value)
    'last_change_date_after' - Card.objects.filter(last_change_date__gte=value)
    'last_change_date_before' - Card.objects.filter(last_change_date__gte=value)
    'ordering': orders the queryset depending on provided value:
      'name' - by name (ascending)
      'name' - by name (descending
      'dishes_count' - by number of dishes (ascending)
      '-dishes_count' - by number of dishes (descending),
    '''
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    filterset_class = CardAPIListFilterSet
    ordering_fields = ['name', 'dishes_count']


class CardAPIDetail(EmenuCardAPIMixin, generics.RetrieveUpdateDestroyAPIView):
    '''
    View, edit or delete specific card using django rest api view
    '''


class EmenuDishAPIMixin():
    '''
    Custom mixin for django-rest Dish views that contains shared data
    '''
    serializer_class = DishSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Dish.objects.all().prefetch_related('cards')


class DishAPIList(EmenuDishAPIMixin, generics.ListCreateAPIView):
    '''
    Create new dish or list all dishes using django rest api view
    '''


class DishAPIDetail(EmenuDishAPIMixin, generics.RetrieveUpdateDestroyAPIView):
    '''
    View, edit or delete specific dish using django rest api view
    '''

