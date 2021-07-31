from copy import copy

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase, SimpleTestCase

from .models import Card, Dish

base_card_kwargs = {
    'name': 'menu {}',
    'description': 'Sample description of the menu card',
    'creation_date': None,
    'last_change_date': None,
}

class CardTestCase(TestCase):
    def setUp(self):
        for i in range(10):
            card_kwargs = copy(base_card_kwargs)
            card_kwargs['name'] = 'menu {}'.format(i)
            Card.objects.get_or_create(**card_kwargs)

    def test_card_name_unique_validation(self):
        menu_1 = Card.objects.get(name='menu 1')
        card_kwargs = copy(base_card_kwargs)
        card_kwargs['name'] = 'menu 1'
        self.assertRaisesMessage(
                expected_exception=IntegrityError,
                expected_message='''duplicate key value violates unique '''
                                 '''constraint "card_card_name_key"''',
                callable=Card.objects.create,
                **card_kwargs,
        )

    def test_card_name_length_validation(self):
        card_kwargs = copy(base_card_kwargs)
        card_kwargs['name'] = 1501 * 'a'
        self.assertRaisesMessage(
                expected_exception=ValidationError,
                expected_message='''Length of {} cannot exceed {} '''
                                 '''characters (current: {})''',
                callable=Card.objects.create,
                **card_kwargs,
        )
        pass
