from datetime import datetime

from django.db.models import Count
from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormMixin

from .forms import CardListForm
from .models import Card, Dish

_fmt_str_to_date = lambda x: datetime(*(int(i) for i in x.split('-')))

def filter_qs_by_str_date(queryset, query_dict, field_name):
    date_as_str = query_dict.get(field_name, None)
    if not date_as_str:
        return queryset
    date = _fmt_str_to_date(date_as_str)
    return queryset.filter(**{field_name: date})

class CardListView(FormMixin, ListView):
    form_class = CardListForm
    model = Card
    template_name = 'card_list.html'

    def filter_queryset(self, queryset):
        query_dict = self.request.GET

        name = query_dict.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)

        queryset = filter_qs_by_str_date(
                queryset, query_dict, 'creation_date__lte',
        )
        queryset = filter_qs_by_str_date(
                queryset, query_dict, 'creation_date__gte',
        )
        queryset = filter_qs_by_str_date(
                queryset, query_dict, 'last_change_date__lte',
        )
        queryset = filter_qs_by_str_date(
                queryset, query_dict, 'last_change_date__gte',
        )

        order_by = query_dict.get('order_by', None)
        if order_by:
            if 'dishes' in order_by:
                queryset = queryset.annotate(dishes_count=Count('dish'))
            queryset = queryset.order_by(order_by)
        return queryset
        
    #TODO hide empty cards if not authorized
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('dishes')
        queryset = self.filter_queryset(queryset)
        return queryset

class CardDetailView(DetailView):
    model = Card
    template_name = 'card_detail.html'
