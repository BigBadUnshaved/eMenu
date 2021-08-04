from datetime import timedelta, datetime

from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from django.core.management import BaseCommand
from django.utils.timezone import now

from card.models import Dish


EMAIL_NO_CHANGES_TEMPLATE = '''
Good morning!

We would like to report there have been no changes to the dishes in eMenu

Have a nice day,
eMenu
'''

EMAIL_REPORT_TEMPLATE = '''
Good morning!

Here is the list of dishes changed yesterday: 
{}

Have a nice day,
eMenu
'''

EMAIL_FROM = 'admin@emenu.com'

def get_boundry_dates():
    '''
    Return two boundry dates, to filter queryset where datetime field
    contains yesterday date.
    '''
    current = now()
    today_kwargs = {i: getattr(current, i) for i in ['year', 'month', 'day',]}
    today_kwargs.update({'hour': 0, 'minute': 0, 'second': 0, 'microsecond': 0})
    today = datetime(**today_kwargs)
    yesterday = today - timedelta(days=1)
    return yesterday, today

def generate_user_emails(user_qs=None):
    '''
    Return generator containing users' emails in str format.
    '''
    if user_qs is None:
        user_qs = User.objects.exclude(email='')
    return (str(user.email) for user in user_qs)

def get_dish_report_line(dish):
    '''
    Return line for specific dish to be included in report
    '''
    cards = dish.cards.all()
    cards_str = ', '.join((str(card) for card in cards))
    if len(cards) > 1:
        suffix = 'found on menu cards: {}'.format(cards_str)
    elif len(cards) == 1:
        suffix = 'found on menu card: {}'.format(cards_str)
    else:
        suffix = 'not currently found on any menu cards'
    line = '{} {}'
    return line.format(dish, suffix)

class Command(BaseCommand):
    help = '''Send e-mail to all users with a list of dishes '''\
           '''that were changed or added yesterday'''

    def handle(self, *args, **options):
        user_qs = User.objects.exclude(email='')
        if len(user_qs) == 0:
            self.stdout.write('No users to send report to')
            return

        yesterday, today = get_boundry_dates()
        dish_qs = Dish.objects\
            .filter(last_change_date__range=(yesterday, today))\
            .prefetch_related('cards')

        subject = 'Daily eMenu report'
        _dish_str = lambda dish: '{} found on card(s) {}'.format
        if len(dish_qs) > 0:
            message = EMAIL_REPORT_TEMPLATE.format(
                '\n'.join(get_dish_report_line(dish) for dish in dish_qs)
            )
        else:
            message = EMAIL_NO_CHANGES_TEMPLATE

        gen_datatuple = ((subject, message, EMAIL_FROM, [user])
                         for user in generate_user_emails(user_qs))
        send_mass_mail(tuple(tuple(i) for i in gen_datatuple))
        self.stdout.write('Email report send to users')
