from copy import copy
from datetime import datetime, timedelta
from decimal import Decimal
from pytz import timezone
from unittest import mock

from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.utils.timezone import get_current_timezone, now

def get_current_datetime():
    return datetime.now(timezone('Europe/Warsaw'))

def initial_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Card = apps.get_model('card', 'Card')
    Dish = apps.get_model('card', 'Dish')
    base_user_kwargs = {
        'username': '{}',
        'first_name': '',
        'last_name': '',
        'password': 'T3stP4ss{}',
        'email': '{}@example.com',
    }
    base_card_kwargs = {
        'name': 'Menu {}',
        'description': 'Sample description of the menu card',
        'creation_date': None,
        'last_change_date': None,
    }
    base_dish_kwargs = {
        'name': 'Dish {}',
        'description': 'Sample description of a dish',
        'price': Decimal('0'),
        'preparation_time': 0,
        'is_vegetarian': False,
        'creation_date': None,
        'last_change_date': None,
    }
    dish_map = {}
    for i in range(1, 21):
        card_kwargs = copy(base_card_kwargs)
        card_kwargs['name'] = 'Menu {}'.format(i)
        dish_kwargs = copy(base_dish_kwargs)
        dish_kwargs['name'] = 'Dish {}'.format(i)
        dish_kwargs['price'] += Decimal(i)
        dish_kwargs['preparation_time'] += i
        dish_kwargs['is_vegetarian'] = i < 10

        delta = 1 if dish_kwargs['is_vegetarian'] else i
        mock_date = get_current_datetime() - timedelta(days=delta)
        with mock.patch('django.utils.timezone.now',
                        mock.Mock(return_value=mock_date)):
            card = Card.objects.create(**card_kwargs)
            dish = Dish.objects.create(**dish_kwargs)

        dish_map[i] = dish
        card.dishes.add(*(dish_map[j] for j in range(2, i)))
    for i in ['user_1', 'user_2', 'user_3']:
        user_kwargs = copy(base_user_kwargs)
        user_kwargs['username'] = user_kwargs['username'].format(i)
        user_kwargs['email'] = user_kwargs['email'].format(i)
        password = make_password(user_kwargs['password'].format(i[-1]))
        user_kwargs['password'] = password
        user = User.objects.create(**user_kwargs)


class Migration(migrations.Migration):

    dependencies = [
        ('card', '0002_dish_is_vegetarian'),
    ]

    operations = [
        migrations.RunPython(initial_data),
    ]
