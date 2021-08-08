import json

from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.filters import OrderingFilter
from card import api_views

from card.serializers import (CardSerializer, CardDetailSerializer,
    CardListSerializer, DishSerializer)


class EmenuRenderer(BrowsableAPIRenderer):
    '''
    BrowsableAPIRenderer modified to be used with custom template
    using syntax more similar to Django class based views
    '''
    def __init__(self, template_name=None, *args, **kwargs):
        self.template=template_name
        return super().__init__(*args, **kwargs)

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        content = context.get('content', '')
        if content.strip() == '':
            return context
        content = json.loads(context.get('content', '{}'))
        object_list = content.get('results', [])
        if object_list:
            context['object_list'] = object_list
        else:
            context['object'] = content
        return context


class EmenuMixin():
    '''
    Mixin to overwrite template used by BrowsableAPIRenderer
    '''
    template_name = None

    def get_renderers(self, *args, **kwargs):
        if self.template_name:
            return [EmenuRenderer(self.template_name)]
        return super().get_renderers(*args, **kwargs)


class EmenuSingleObjectMixin(EmenuMixin):
    '''
    Version of EmenuMixin modified for views dedicated to a single object
    '''
    #TODO - get rid of this awfulness and find better way to get form init data
    def get_serializer(self, *args, **kwargs):
        instance = self.get_object()
        kwargs['instance'] = self.get_object()
        try:
            return super().get_serializer(*args, **kwargs)
        except TypeError as e:
            msg = "__init__() got multiple values for argument 'instance'"
            if str(e) == msg:
                kwargs.pop('instance')
                return super().get_serializer(*args, **kwargs)
            raise e


class CardListView(EmenuMixin, api_views.CardAPIList):
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
    template_name = 'card_list.html'


class CardCreateView(CardListView):
    '''
    View to create new card menu objects
    '''
    serializer_class = CardDetailSerializer
    template_name = 'edit_form.html'


class CardDetailView(EmenuSingleObjectMixin,
        api_views.EmenuCardAPIMixin, generics.RetrieveDestroyAPIView):
    '''
    View to view detail and delete specific card menu object
    '''
    serializer_class = CardDetailSerializer
    template_name = 'card_detail.html'


class CardUpdateView(EmenuSingleObjectMixin,
        api_views.EmenuCardAPIMixin, generics.UpdateAPIView):
    '''
    View to edit specific card menu
    '''
    serializer_class = CardDetailSerializer
    template_name = 'edit_form.html'
