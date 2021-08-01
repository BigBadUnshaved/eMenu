from copy import copy
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.utils import DataError, IntegrityError
from django.test import TestCase, SimpleTestCase

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
