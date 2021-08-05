from copy import copy
from datetime import datetime, timedelta
from decimal import Decimal
from itertools import chain
import json
from pytz import timezone
from unittest import mock

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.db.utils import DataError, IntegrityError
from django.test import TestCase, RequestFactory

from .models import Card, Dish
from card import views, api_views


TIME_ZONE = getattr(settings, 'TIME_ZONE', 'Europe/Warsaw')

base_user_kwargs = {
    'username': 'test_user_{}',
    'first_name': '',
    'last_name': '',
    'email': 'user_{}@example.com',
    'password': 'T3stP4ss{}',
}
base_card_kwargs = {
    'name': 'test menu {}',
    'description': 'Sample description of the menu card',
    'creation_date': None,
    'last_change_date': None,
}
base_dish_kwargs = {
    'name': 'test dish {}',
    'description': 'Sample description of a dish',
    'price': Decimal('0'),
    'preparation_time': 0,
    'is_vegetarian': False,
    'creation_date': None,
    'last_change_date': None,
}

def get_current_datetime():
    return datetime.now(timezone(TIME_ZONE))

def datetime_to_get_param(date):
    return date.strftime('%Y-%m-%d')

def str_date_to_datetime(str_date):
    str_date, str_time = str_date[:10], str_date[12:19]
    date_args = chain(str_date.split('-'), str_time.split(':'))
    int_list = (int(i) for i in date_args)
    return datetime(*int_list, tzinfo=timezone(TIME_ZONE))

def create_cards(arg, card_list):
    card_kwargs = copy(base_card_kwargs)
    card_kwargs['name'] = 'test menu {}'.format(arg)
    card = Card.objects.get_or_create(**card_kwargs)[0]
    card_list.append(card)

def create_dishes(arg, card_list):
    dish_kwargs = copy(base_dish_kwargs)
    dish_kwargs['name'] = 'test dish {}'.format(arg)
    dish = Dish.objects.get_or_create(**dish_kwargs)[0]
    if card_list:
        dish.cards.add(*card_list)

def create_users(arg, card_list):
    user_kwargs = copy(base_user_kwargs)
    user_kwargs['username'] = 'test_user_{}'.format(arg)
    user_kwargs['email'] = 'user{}@example.com'.format(arg)
    user_kwargs['password'] = make_password('T3stP4ss{}'.format(arg))
    User.objects.get_or_create(**user_kwargs)


def get_init_data(dishes=True, cards=True, users=True):
    function_list = []
    if dishes == True:
        function_list.append(create_dishes)
    if cards == True:
        function_list.append(create_cards)
    if users == True:
        function_list.append(create_users)
    card_list = []
    for i in range(1, 3):
        for func in function_list:
            func(i, card_list)

def get_values_from_json(json_response, value):
    return [i[value] for i in json_response['results']]


class CardTestCase(TestCase):
    def setUp(self):
        get_init_data(users=False)

    def test_card_name_unique_validation(self):
        card_kwargs = copy(base_card_kwargs)
        card_kwargs['name'] = 'test menu 1'
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
        card = Card.objects.get(name='test menu 1')
        now = get_current_datetime()
        card.creation_date = now
        card.save()
        post_save = Card.objects.get(name='test menu 1')
        self.assertEqual(card.creation_date, post_save.creation_date)

    def test_card_last_change_date_auto_now_true(self):
        card = Card.objects.get(name='test menu 1')
        now = get_current_datetime()
        with mock.patch('django.utils.timezone.now',
                        mock.Mock(return_value=now)):
            card.save()
            self.assertEqual(card.last_change_date, now)

    def test_card_last_change_date_editable_false(self):
        card = Card.objects.get(name='test menu 1')
        now = get_current_datetime()
        with mock.patch('django.utils.timezone.now',
                        mock.Mock(return_value=now)):
            card.last_change_date = now + timedelta(5)
            card.save()
            self.assertEqual(card.last_change_date, now)


class DishTestCase(TestCase):
    def setUp(self):
        get_init_data(users=False)

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
        dish = Dish.objects.get(name='test dish 1')
        now = get_current_datetime()
        dish.creation_date = now
        dish.save()
        post_save = Dish.objects.get(name='test dish 1')
        self.assertEqual(dish.creation_date, post_save.creation_date)

    def test_dish_last_change_date_auto_now_true(self):
        dish = Dish.objects.get(name='test dish 1')
        now = get_current_datetime()
        with mock.patch('django.utils.timezone.now',
                        mock.Mock(return_value=now)):
            dish.save()
            self.assertEqual(dish.last_change_date, now)

    def test_dish_last_change_date_editable_false(self):
        dish = Dish.objects.get(name='test dish 1')
        now = get_current_datetime()
        with mock.patch('django.utils.timezone.now',
                        mock.Mock(return_value=now)):
            dish.last_change_date = now + timedelta(5)
            dish.save()
            self.assertEqual(dish.last_change_date, now)

    def test_dish_price_positive_value(self):
        dish = Dish.objects.get(name='test dish 1')
        dish.price = Decimal(-10)
        expected_message = 'Price cannot be lower then 0.00'
        with self.assertRaisesMessage(ValidationError, expected_message):
            dish.save()

    def test_dish_preparation_time_positive_value(self):
        dish = Dish.objects.get(name='test dish 1')
        dish.preparation_time = -10
        expected_message = '''new row for relation "card_dish" violates ''' \
                           '''check constraint ''' \
                           '''"card_dish_preparation_time_check"'''
        with self.assertRaisesMessage(IntegrityError, expected_message):
            dish.save()

    def test_dish_is_vegetarian_default_false(self):
        dish_kwargs = copy(base_dish_kwargs)
        dish_kwargs['name'] = 'test dish 2'
        dish_kwargs.pop('is_vegetarian')
        dish = Dish.objects.create(**dish_kwargs)
        self.assertEqual(dish.is_vegetarian, False)


class CardAPIListTest(TestCase):
    def setUp(self):
        get_init_data(dishes=False, cards=False)
        self.factory = RequestFactory()
        self.logged_user = User.objects.get(username='test_user_1')

    def test_list_exclude_cards_with_no_dishes_for_unauthorized_users(self):
        results = []
        for user in [self.logged_user, AnonymousUser()]:
            request = self.factory.get('/api/cards/')
            request.user = user
            response = api_views.CardAPIList.as_view()(request)
            content_json = json.loads(response.rendered_content)
            results.append(content_json['count'])
        self.assertNotEqual(results[0], results[1])

    def test_list_filter_name(self):
        request = self.factory.get('/api/cards/?name=Menu+1')
        request.user = self.logged_user
        response = api_views.CardAPIList.as_view()(request)
        content_json = json.loads(response.rendered_content)
        name_list = get_values_from_json(content_json, 'name')
        self.assertEqual(len(name_list), 1)
        self.assertEqual(name_list[0], 'Menu 1')

    def test_list_filter_creation_date_range(self):
        now = get_current_datetime()
        yesterday = now - timedelta(days=1)
        after_str = datetime_to_get_param(yesterday)
        before_str = datetime_to_get_param(now)
        url = '/api/cards/?creation_date_after={}&creation_date_before={}'
        request = self.factory.get(url.format(after_str, before_str))
        request.user = self.logged_user
        response = api_views.CardAPIList.as_view()(request)
        content_json = json.loads(response.rendered_content)
        creation_date_str_list = get_values_from_json(
                content_json, 'creation_date'
        )
        for str_date in creation_date_str_list:
            date = str_date_to_datetime(str_date).date()
            self.assertEqual(date>=yesterday.date(), True)
            self.assertEqual(date<=now.date(), True)

    def test_list_filter_last_change_date_range(self):
        now = get_current_datetime()
        yesterday = now - timedelta(days=1)
        after_str = datetime_to_get_param(yesterday)
        before_str = datetime_to_get_param(now)
        url = '/api/cards/?last_change_date_after={}&last_change_date_before={}'
        request = self.factory.get(url.format(after_str, before_str))
        request.user = self.logged_user
        response = api_views.CardAPIList.as_view()(request)
        content_json = json.loads(response.rendered_content)
        creation_date_str_list = get_values_from_json(
                content_json, 'last_change_date'
        )
        for str_date in creation_date_str_list:
            date = str_date_to_datetime(str_date).date()
            self.assertEqual(date>=yesterday.date(), True)
            self.assertEqual(date<=now.date(), True)

    def test_list_ordering_name_asc(self):
        request = self.factory.get('/api/cards/?ordering=name')
        request.user = self.logged_user
        response = api_views.CardAPIList.as_view()(request)
        content_json = json.loads(response.rendered_content)
        name_list = get_values_from_json(content_json, 'name')
        self.assertEqual(name_list, sorted(name_list))

    def test_list_ordering_name_desc(self):
        request = self.factory.get('/api/cards/?ordering=-name')
        request.user = self.logged_user
        response = api_views.CardAPIList.as_view()(request)
        content_json = json.loads(response.rendered_content)
        name_list = get_values_from_json(content_json, 'name')
        self.assertEqual(name_list, sorted(name_list, reverse=True))

    def test_list_ordering_dishes_count_asc(self):
        request = self.factory.get('/api/cards/?ordering=dishes_count')
        request.user = self.logged_user
        response = api_views.CardAPIList.as_view()(request)
        content_json = json.loads(response.rendered_content)
        dishes_count_list = get_values_from_json(content_json, 'dishes_count')
        self.assertEqual(dishes_count_list, sorted(dishes_count_list))

    def test_list_ordering_dishes_count_desc(self):
        request = self.factory.get('/api/cards/?ordering=-dishes_count')
        request.user = self.logged_user
        response = api_views.CardAPIList.as_view()(request)
        content_json = json.loads(response.rendered_content)
        content_json = json.loads(response.rendered_content)
        dishes_count_list = get_values_from_json(content_json, 'dishes_count')
        self.assertEqual(
                dishes_count_list, sorted(dishes_count_list, reverse=True)
        )

    def test_list_create_permission_check(self):
        data = {
            'name': 'I should not exist',
            'description': 'test_list_create_permission_check went wrong'
        }
        request = self.factory.post('/api/cards/', data=data)
        request.user = AnonymousUser()
        response = api_views.CardAPIList.as_view()(request)
        self.assertEqual(response.status_code, 403)


class CardAPIDetailTest(TestCase):
    def setUp(self):
        get_init_data(dishes=False, cards=False)
        self.factory = RequestFactory()
        self.logged_user = User.objects.get(username='test_user_1')

    def test_detail_permission_check(self):
        data = {
            'name': 'I should not exist',
            'description': 'test_detail_permission_check went wrong'
        }
        request = self.factory.put('/api/cards/1', data=data)
        request.user = AnonymousUser()
        response = api_views.CardAPIList.as_view()(request)
        self.assertEqual(response.status_code, 403)


class CardListTest(TestCase):
    def setUp(self):
        get_init_data(dishes=False, cards=False)
        self.factory = RequestFactory()
        self.logged_user = User.objects.get(username='test_user_1')

    def test_list_exclude_cards_with_no_dishes_for_unauthorized_users(self):
        results = []
        for user in [self.logged_user, AnonymousUser()]:
            request = self.factory.get('/card/')
            request.user = user
            response = views.CardListView.as_view()(request)
            object_list = response.context_data.get(
                    'object_list', Card.objects.none
            )
            results.append(len(object_list))
        self.assertNotEqual(results[0], results[1])

    def test_list_filter_name(self):
        request = self.factory.get('/card/?name=Menu+1')
        request.user = self.logged_user
        response = views.CardListView.as_view()(request)
        object_list = response.context_data.get(
                'object_list', Card.objects.none
        )
        name_list = object_list.values_list('name', flat=True)
        for name in name_list:
            self.assertNotEqual(name.lower().find('menu 1'), -1)

    def test_list_filter_creation_date_range(self):
        now = get_current_datetime()
        yesterday = now - timedelta(days=1)
        after_str = datetime_to_get_param(yesterday)
        before_str = datetime_to_get_param(now)
        url = '/card/?creation_date__gte={}&creation_date__lte={}'
        request = self.factory.get(url.format(after_str, before_str))
        request.user = self.logged_user
        response = views.CardListView.as_view()(request)
        object_list = response.context_data.get(
                'object_list', Card.objects.none
        )

        for obj in object_list:
            date = obj.creation_date.date()
            self.assertEqual(date>=yesterday.date(), True)
            self.assertEqual(date<=now.date(), True)

    def test_list_filter_last_change_date_range(self):
        now = get_current_datetime()
        yesterday = now - timedelta(days=1)
        after_str = datetime_to_get_param(yesterday)
        before_str = datetime_to_get_param(now)
        url = '/card/?last_change_date__gte={}&last_change_date__lte={}'
        request = self.factory.get(url.format(after_str, before_str))
        request.user = self.logged_user
        response = views.CardListView.as_view()(request)
        object_list = response.context_data.get(
                'object_list', Card.objects.none
        )

        for obj in object_list:
            date = obj.last_change_date.date()
            self.assertEqual(date>=yesterday.date(), True)
            self.assertEqual(date<=now.date(), True)

    def test_list_ordering_name_asc(self):
        request = self.factory.get('/card/?order_by=name')
        request.user = self.logged_user
        response = views.CardListView.as_view()(request)
        object_list = response.context_data.get(
                'object_list', Card.objects.none
        )
        name_list = list(object_list.values_list('name', flat=True))
        self.assertEqual(name_list, sorted(name_list))

    def test_list_ordering_name_desc(self):
        request = self.factory.get('/card/?order_by=-name')
        request.user = self.logged_user
        response = views.CardListView.as_view()(request)
        object_list = response.context_data.get(
                'object_list', Card.objects.none
        )
        name_list = list(object_list.values_list('name', flat=True))
        self.assertEqual(name_list, sorted(name_list, reverse=True))

    def test_list_ordering_dishes_count_asc(self):
        request = self.factory.get('/card/?order_by=dishes_count')
        request.user = self.logged_user
        response = views.CardListView.as_view()(request)
        object_list = response.context_data.get(
                'object_list', Card.objects.none
        )
        dishes_count_list = list(object_list\
                .annotate(dishes_count=Count('dishes'))\
                .values_list('dishes_count', flat=True)
        )
        self.assertEqual(dishes_count_list, sorted(dishes_count_list))

    def test_list_ordering_dishes_count_desc(self):
        request = self.factory.get('/card/?order_by=-dishes_count')
        request.user = self.logged_user
        response = views.CardListView.as_view()(request)
        object_list = response.context_data.get(
                'object_list', Card.objects.none
        )
        dishes_count_list = list(object_list\
                .annotate(dishes_count=Count('dishes'))\
                .values_list('dishes_count', flat=True)
        )
        self.assertEqual(
                dishes_count_list,
                sorted(dishes_count_list, reverse=True)
        )

