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

EMAIL_FROM = ''

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

def generate_user_emails():
    '''
    Return generator containing users' emails in str format.
    '''
    user_qs = User.objects.exclude(email='')
    return (str(user.email) for user in user_qs)

class Command(BaseCommand):
    help = '''Send e-mail to all users with a list of new '''\
           '''and changed dishes during last 24 hours. '''

    def handle(self, *args, **options):
        yesterday, today = get_boundry_dates()
        dish_qs = Dish.objects\
            .filter(last_change_date__range=(yesterday, today))\
            .prefetch_related('cards')

        subject = 'Daily eMenu report'
        if len(dish_qs) > 0:
            message = EMAIL_REPORT_TEMPLATE.format(
                '\n'.join('{} found on card(s): {}'.format(
                    dish, ', '.join(dish.cards.call() for dish in dish_qs)
                ))
            )
        else:
            message = EMAIL_NO_CHANGES_TEMPLATE

        gen_datatuple = ((subject, message, EMAIL_FROM, [user])
                         for user in generate_user_emails())
        send_mass_mail(tuple(tuple(i) for i in gen_datatuple))
