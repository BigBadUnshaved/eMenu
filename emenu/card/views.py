from datetime import datetime
from re import match

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.db.models.functions import Lower
from django.forms import CharField
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView,
        ListView, UpdateView)
from django.views.generic.edit import FormMixin

from .forms import CardListForm
from .models import Card, Dish

def fmt_str_to_date(date_as_str):
    '''
    Creates datetime from a string in one of the following formats:
    YYYY
    YYYY-MM
    YYYY-MM-DD
    YYYY-MM-DD-HH
    YYYY-MM-DD-HH-MM
    YYYY-MM-DD-HH-MM-SS
    '''
    args = [int(i) for i in date_as_str.split('-')]
    while len(args) < 3:
        args.append(1)
    return datetime(*args)

def validate_date_format(date):
    '''
    Valide function to see if given string can be used to create datetime 
    ("-" is the expected seperator)
    '''
    regex_pattern = '[0-9]{4}(-[0-9]{1,2}){0,4}'
    date = date.replace(' ', '')
    date_match = match(regex_pattern, date)
    if not date_match:
        msg = "Please enter date in following format: YYYY-MM-DD"
        raise ValidationError(msg)

def filter_qs_by_str_date(queryset, request, field_name):
    '''
    Helper function that runs validation of dates provided by user 
    and filters queryset
    '''
    query_dict = request.GET
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
    '''
    Custom mixin to enforce same redirect login_url for different views
    '''
    login_url = '/login/'


class NoStripMixin(EmenuLoginRequiredMixin):
    '''
    Custom mixin to turn off strip generated by Django on CharFields
    '''
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
    '''
    List all menu cards using django generic view; 
    accepts following get parameters:
    'name' - equal to Card.objects.filter(name__icontains=value)
    'creation_date__gte' - Card.objects.filter(creation_date__gte=value)
    'creation_date__lte' - Card.objects.filter(creation_date__gte=value)
    'last_change_date__gte' - Card.objects.filter(last_change_date__gte=value)
    'last_change_date__lte' - Card.objects.filter(last_change_date__gte=value)
    'order_by': orders the queryset depending on provided value:
      'alph_name' - alphabetically by name (ascending)
      '-alph_name' - alphabetically by name (descending
      'dishes_count' - by number of dishes (ascending)
      '-dishes_count' - by number of dishes (descending),
    '''
    form_class = CardListForm
    model = Card
    template_name = 'card_list.html'

    def order_queryset(self, queryset, query_dict):
        '''
        Orders the queryset depending on value of 'order_by' get parameter:
        'alph_name' - alphabetically by name (ascending)
        '-alph_name' - alphabetically by name (descending
        'dishes_count' - by number of dishes (ascending)
        '-dishes_count' - by number of dishes (descending),
        '''
        order_by = query_dict.get('order_by', None)
        if not order_by:
            return queryset
        if 'dishes' in order_by:
            queryset = queryset.annotate(dishes_count=Count('dishes'))
        if 'alph_name' in order_by:
            queryset = queryset.annotate(alph_name=Lower('name'))
        return queryset.order_by(order_by)

    def filter_queryset(self, queryset):
        '''
        Filters the queryset depending on get parameter and it's value
         'name' - equal to Card.objects.filter(name__icontains=value)
         'creation_date__gte' - Card.objects.filter(creation_date__gte=value)
         'creation_date__lte' - Card.objects.filter(creation_date__gte=value)
         'last_change_date__gte' - Card.objects.filter(last_change_date__gte=value)
         'last_change_date__lte' - Card.objects.filter(last_change_date__gte=value)
        '''
        query_dict = self.request.GET

        name = query_dict.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)

        queryset = filter_qs_by_str_date(
                queryset, self.request, 'creation_date__lte',
        )
        queryset = filter_qs_by_str_date(
                queryset, self.request, 'creation_date__gte',
        )
        queryset = filter_qs_by_str_date(
                queryset, self.request, 'last_change_date__lte',
        )
        queryset = filter_qs_by_str_date(
                queryset, self.request, 'last_change_date__gte',
        )
        queryset = self.order_queryset(queryset, query_dict)
        return queryset

    def get_queryset(self):
        '''
        Overwritten to ensure queryset is filtered and ordered
        additionaly, if user is not authenticated we exclude 
        cards with no dishes
        '''
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(dishes__isnull=False)
        queryset = queryset.prefetch_related('dishes')
        return self.filter_queryset(queryset).distinct()


class CardDetailView(DetailView):
    '''
    View specific card using django generic view
    '''
    model = Card
    template_name = 'card_detail.html'


class CardCreateView(NoStripMixin, CreateView):
    '''
    Create new card using django generic view
    '''
    model = Card
    fields = ['name', 'description']
    template_name = 'edit_form.html'


class CardUpdateView(NoStripMixin, UpdateView):
    '''
    Edit existing card using django generic view
    '''
    model = Card
    fields = ['name', 'description']
    template_name = 'edit_form.html'


class CardDeleteView(EmenuLoginRequiredMixin, DeleteView):
    '''
    Delete card using django generic view
    '''
    model = Card
    success_url = reverse_lazy('card-list')
    template_name = 'confirm_delete.html'


class DishListView(NoStripMixin, ListView):
    '''
    List all dishes using django generic view
    '''
    model = Dish
    template_name = 'dish_list.html'


class DishDetailView(EmenuLoginRequiredMixin, DetailView):
    '''
    View specific dish using django generic view
    '''
    model = Dish
    template_name = 'dish_detail.html'


class DishCreateView(NoStripMixin, CreateView):
    '''
    Create new dish using django generic view
    '''
    model = Dish
    fields = [
        'name', 'description', 'price', 'preparation_time',
        'cards', 'is_vegetarian', 
    ]
    template_name = 'edit_form.html'


class DishUpdateView(NoStripMixin, UpdateView):
    '''
    Edit specific dish using django generic view
    '''
    model = Dish
    fields = [
        'name', 'description', 'price', 'preparation_time',
        'cards', 'is_vegetarian', 
    ]
    template_name = 'edit_form.html'


class DishDeleteView(EmenuLoginRequiredMixin, DeleteView):
    '''
    Delete specific dish using django generic view
    '''
    model = Dish
    success_url = reverse_lazy('dish-list')
    template_name = 'confirm_delete.html'

