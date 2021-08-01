from copy import copy
from decimal import Decimal

from django.db import migrations

def initial_data(apps, schema_editor):
    Card = apps.get_model('card', 'Card')
    Dish = apps.get_model('card', 'Dish')
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
        card = Card.objects.create(**card_kwargs)

        dish_kwargs = copy(base_dish_kwargs)
        dish_kwargs['name'] = 'Dish {}'.format(i)
        dish_kwargs['price'] += Decimal(i)
        dish_kwargs['preparation_time'] += i
        dish_kwargs['is_vegetarian'] = i < 10
        dish = Dish.objects.create(**dish_kwargs)
        dish_map[i] = dish

        for j in range(1, i):
            card.dishes.add(dish_map[j])
            

class Migration(migrations.Migration):

    dependencies = [
        ('card', '0002_dish_is_vegetarian'),
    ]

    operations = [
        migrations.RunPython(initial_data),
    ]
