import json

from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.filters import OrderingFilter
from card import api_views

from card.serializers import (CardSerializer, CardDetailSerializer,
    CardListSerializer, DishSerializer)


class EmenuRenderer(BrowsableAPIRenderer):
    def __init__(self, template_name=None, *args, **kwargs):
        self.template=template_name
        return super().__init__(*args, **kwargs)

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        content = json.loads(context.get('content', '{}'))
        object_list = content.get('results', [])
        for i in object_list:
            for k, v in i.items():
                print(k, v)
        if object_list:
            context['object_list'] = object_list
            if len(object_list) == 1:
                context['object'] = object_list[0]
        return context


class EmenuMixin():
    template_name = None

    def get_renderers(self, *args, **kwargs):
        if self.template_name:
            return [EmenuRenderer(self.template_name)]
        return super().get_renderers(*args, **kwargs)


class CardListView(EmenuMixin, api_views.EmenuCardAPIMixin, generics.ListAPIView):
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
    serializer_class = CardListSerializer
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    filterset_class = api_views.CardAPIListFilterSet
    ordering_fields = ['name', 'dishes_count']
    template_name = 'card_list.html'
