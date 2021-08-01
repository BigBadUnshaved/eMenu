from copy import copy
from datetime import datetime, timedelta
from decimal import Decimal
from pytz import timezone
from unittest import mock

from django.core.exceptions import ValidationError
from django.db.utils import DataError, IntegrityError
from django.test import TestCase

from .models import Card, Dish

base_card_kwargs = {
    'name': 'menu {}',
    'description': 'Sample description of the menu card',
    'creation_date': None,
    'last_change_date': None,
}
base_dish_kwargs = {
    'name': 'dish {}',
    'description': 'Sample description of a dish',
    'price': Decimal('0'),
    'preparation_time': 0,
    'is_vegetarian': False,
    'creation_date': None,
    'last_change_date': None,
}

def get_current_datetime():
    return datetime.now(timezone('Europe/Warsaw'))

class CardTestCase(TestCase):
    def setUp(self):
        for i in range(2):
            card_kwargs = copy(base_card_kwargs)
            card_kwargs['name'] = 'menu {}'.format(i)
            Card.objects.get_or_create(**card_kwargs)

    def test_card_name_unique_validation(self):
        card_kwargs = copy(base_card_kwargs)
        card_kwargs['name'] = 'menu 0'
        expected_message = '''duplicate key value violates unique ''' \
                           '''constraint "card_card_name_key"''' 
        with self.assertRaisesMessage(IntegrityError, expected_message):
            Card.objects.create(**card_kwargs)

    def test_card_name_length_validation(self):
        card_kwargs = copy(base_card_kwargs)
        card_kwargs['name'] = 51 * 'a'
        expected_message = 'value too long for type character varying(50)'
        with self.assertRaisesMessage(DataError, expected_message):
            Card.objects.create(**card_kwargs)
        

    def test_card_description_length_validation(self):
        card_kwargs = copy(base_card_kwargs)
        card_kwargs['description'] = 1501 * 'a'
        expected_message = '''Length of {} cannot exceed {} ''' \
                           '''characters (current: {})'''
        expected_message = expected_message.format(
            'description',
            '1500',
            len(card_kwargs['description']),
        )
        with self.assertRaisesMessage(ValidationError, expected_message):
            Card.objects.create(**card_kwargs)

    def test_card_creation_date_auto_now_add_true(self):
        card_kwargs = copy(base_card_kwargs)
        card_kwargs['name'] = 'menu 2'
        now = get_current_datetime()
        with mock.patch('django.utils.timezone.now',
                        mock.Mock(return_value=now)):
            card = Card.objects.create(**card_kwargs)
            self.assertEqual(card.creation_date, now)

    def test_card_creation_date_editable_false(self):
        card = Card.objects.get(name='menu 0')
        now = get_current_datetime()
        card.creation_date = now
        card.save()
        post_save = Card.objects.get(name='menu 0')
        self.assertEqual(card.creation_date, post_save.creation_date)

    def test_card_last_change_date_auto_now_true(self):
        card = Card.objects.get(name='menu 0')
        now = get_current_datetime()
        with mock.patch('django.utils.timezone.now',
                        mock.Mock(return_value=now)):
            card.save()
            self.assertEqual(card.last_change_date, now)

    def test_card_last_change_date_editable_false(self):
        card = Card.objects.get(name='menu 0')
        now = get_current_datetime()
        with mock.patch('django.utils.timezone.now',
                        mock.Mock(return_value=now)):
            card.last_change_date = now + timedelta(5)
            card.save()
            self.assertEqual(card.last_change_date, now)

class DishTestCase(TestCase):
    def setUp(self):
        for i in range(2):
            card_kwargs = copy(base_card_kwargs)
            dish_kwargs = copy(base_dish_kwargs)
            card_kwargs['name'] = 'menu {}'.format(i)
            dish_kwargs['name'] = 'dish {}'.format(i)
            Card.objects.get_or_create(**card_kwargs)
            Dish.objects.get_or_create(**dish_kwargs)

    def test_dish_name_length_validation(self):
        dish_kwargs = copy(base_dish_kwargs)
        dish_kwargs['name'] = 51 * 'a'
        expected_message = 'value too long for type character varying(50)'
        with self.assertRaisesMessage(DataError, expected_message):
            Dish.objects.create(**dish_kwargs)

    def test_dish_description_length_validation(self):
        dish_kwargs = copy(base_dish_kwargs)
        dish_kwargs['description'] = 1501 * 'a'
        expected_message = '''Length of {} cannot exceed {} ''' \
                           '''characters (current: {})'''
        expected_message = expected_message.format(
            'description',
            '1500',
            len(dish_kwargs['description']),
        )
        with self.assertRaisesMessage(ValidationError, expected_message):
            Dish.objects.create(**dish_kwargs)

    def test_dish_creation_date_auto_now_add_true(self):
        dish_kwargs = copy(base_dish_kwargs)
        dish_kwargs['name'] = 'dish 2'
        now = get_current_datetime()
        with mock.patch('django.utils.timezone.now',
                        mock.Mock(return_value=now)):
            dish = Dish.objects.create(**dish_kwargs)
            self.assertEqual(dish.creation_date, now)

    def test_dish_creation_date_editable_false(self):
        dish = Dish.objects.get(name='dish 0')
        now = get_current_datetime()
        dish.creation_date = now
        dish.save()
        post_save = Dish.objects.get(name='dish 0')
        self.assertEqual(dish.creation_date, post_save.creation_date)

    def test_dish_last_change_date_auto_now_true(self):
        dish = Dish.objects.get(name='dish 0')
        now = get_current_datetime()
        with mock.patch('django.utils.timezone.now',
                        mock.Mock(return_value=now)):
            dish.save()
            self.assertEqual(dish.last_change_date, now)

    def test_dish_last_change_date_editable_false(self):
        dish = Dish.objects.get(name='dish 0')
        now = get_current_datetime()
        with mock.patch('django.utils.timezone.now',
                        mock.Mock(return_value=now)):
            dish.last_change_date = now + timedelta(5)
            dish.save()
            self.assertEqual(dish.last_change_date, now)

    def test_dish_price_positive_value(self):
        dish = Dish.objects.get(name='dish 0')
        dish.price = Decimal(-10)
        expected_message = 'Price cannot be lower then 0.00'
        with self.assertRaisesMessage(ValidationError, expected_message):
            dish.save()

    def test_dish_preparation_time_positive_value(self):
        dish = Dish.objects.get(name='dish 0')
        dish.preparation_time = -10
        expected_message = '''new row for relation "card_dish" violates ''' \
                           '''check constraint ''' \
                           '''"card_dish_preparation_time_check"'''
        with self.assertRaisesMessage(IntegrityError, expected_message):
            dish.save()

    def test_dish_is_vegetarian_default_false(self):
        dish_kwargs = copy(base_dish_kwargs)
        dish_kwargs['name'] = 'dish 2'
        dish_kwargs.pop('is_vegetarian')
        dish = Dish.objects.create(**dish_kwargs)
        self.assertEqual(dish.is_vegetarian, False)
