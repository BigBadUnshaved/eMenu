from datetime import datetime
from re import match

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.db.models.functions import Lower
from django.forms import CharField
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView,
        ListView, UpdateView)
from django.views.generic.edit import FormMixin

from .forms import CardListForm
from .models import Card, Dish

def fmt_str_to_date(date_as_str):
    args = [int(i) for i in date_as_str.split('-')]
    while len(args) < 3:
        args.append(1)
    return datetime(*args)

def validate_date_format(date):
    regex_pattern = '[0-9]{4}(-[0-9]{1,2}){0,4}'
    date = date.replace(' ', '')
    date_match = match(regex_pattern, date)
    if not date_match:
        msg = "Please enter date in following format: YYYY-MM-DD"
        raise ValidationError(msg)

def filter_qs_by_str_date(queryset, query_dict, field_name, request):
    date_as_str = query_dict.get(field_name, None)
    if not date_as_str:
        return queryset
    try:
        validate_date_format(date_as_str)
    except ValidationError as e:
        messages.error(request, e)
        return queryset
    date = fmt_str_to_date(date_as_str)
    return queryset.filter(**{field_name: date})


class EmenuLoginRequiredMixin(LoginRequiredMixin):
    login_url = '/login/'


class NoStripMixin(EmenuLoginRequiredMixin):
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        char_fields = (
            name
            for name, field in form.fields.items()
            if isinstance(field, CharField)
        )
        for name in char_fields:
            form.fields[name].strip = False
        return form


class CardListView(FormMixin, ListView):
    form_class = CardListForm
    model = Card
    template_name = 'card_list.html'

    def order_queryset(self, queryset, query_dict):
        order_by = query_dict.get('order_by', None)
        if not order_by:
            return queryset
        if 'dishes' in order_by:
            queryset = queryset.annotate(dishes_count=Count('dish'))
        if 'alph_name' in order_by:
            queryset = queryset.annotate(alph_name=Lower('name'))
        return queryset.order_by(order_by)

    def filter_queryset(self, queryset):
        query_dict = self.request.GET

        name = query_dict.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)

        queryset = filter_qs_by_str_date(
                queryset, query_dict, 'creation_date__lte', self.request,
        )
        queryset = filter_qs_by_str_date(
                queryset, query_dict, 'creation_date__gte', self.request,
        )
        queryset = filter_qs_by_str_date(
                queryset, query_dict, 'last_change_date__lte', self.request,
        )
        queryset = filter_qs_by_str_date(
                queryset, query_dict, 'last_change_date__gte', self.request,
        )
        queryset = self.order_queryset(queryset, query_dict)
        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(dishes__isnull=False)
        queryset = queryset.prefetch_related('dishes')
        return self.filter_queryset(queryset).distinct()


class CardDetailView(DetailView):
    model = Card
    template_name = 'card_detail.html'


class CardCreateView(NoStripMixin, CreateView):
    model = Card
    fields = ['name', 'description']
    template_name = 'edit_form.html'


class CardUpdateView(NoStripMixin, UpdateView):
    model = Card
    fields = ['name', 'description']
    template_name = 'edit_form.html'


class CardDeleteView(EmenuLoginRequiredMixin, DeleteView):
    model = Card
    success_url = reverse_lazy('card-list')
    template_name = 'confirm_delete.html'


class DishListView(NoStripMixin, ListView):
    model = Dish
    template_name = 'dish_list.html'


class DishDetailView(EmenuLoginRequiredMixin, DetailView):
    model = Dish
    template_name = 'dish_detail.html'


class DishCreateView(NoStripMixin, CreateView):
    model = Dish
    fields = [
        'name', 'description', 'price', 'preparation_time',
        'cards', 'is_vegetarian', 
    ]
    template_name = 'edit_form.html'


class DishUpdateView(NoStripMixin, UpdateView):
    model = Dish
    fields = [
        'name', 'description', 'price', 'preparation_time',
        'cards', 'is_vegetarian', 
    ]
    template_name = 'edit_form.html'


class DishDeleteView(EmenuLoginRequiredMixin, DeleteView):
    model = Dish
    success_url = reverse_lazy('dish-list')
    template_name = 'confirm_delete.html'



from django_filters import rest_framework as filters
from django.shortcuts import get_object_or_404
from rest_framework import status, generics, permissions
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from card.serializers import CardSerializer, DishSerializer

class EmenuCardAPIMixin():
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Card.objects.all()\
                .prefetch_related('dishes')\
                .annotate(dishes_count=Count('dishes'))
        if not self.request.user.is_authenticated:
            queryset = Card.objects.exclude(dishes__isnull=True)
        return queryset


class CardAPIListFilterSet(filters.FilterSet):
    creation_date = filters.DateTimeFromToRangeFilter()
    last_change_date = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Card
        fields = ['name', 'creation_date', 'last_change_date']


class CardAPIList(EmenuCardAPIMixin, generics.ListCreateAPIView):
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    filterset_class = CardAPIListFilterSet
    ordering_fields = ['name', 'dishes_count']


class CardAPITemplateList(EmenuCardAPIMixin, generics.ListCreateAPIView):
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    filterset_class = CardAPIListFilterSet
    ordering_fields = ['name', 'dishes_count']
    template_name = 'card_list2.html'
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return Response({'object_list': self.object_list})


class CardAPIDetail(EmenuCardAPIMixin, generics.RetrieveUpdateDestroyAPIView):
    pass


class EmenuDishAPIMixin():
    queryset = Dish.objects.all().prefetch_related('cards')
    serializer_class = DishSerializer
    permission_classes = [permissions.IsAuthenticated]


class DishAPIList(EmenuDishAPIMixin, generics.ListCreateAPIView): pass


class DishAPIDetail(EmenuDishAPIMixin, generics.RetrieveUpdateDestroyAPIView):
    pass

