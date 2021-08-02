from datetime import timedelta, datetime

from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from django.core.management import BaseCommand
from django.utils.timezone import now

from card.models import Dish

EMAIL_NO_CHANGES_TEMPLATE = '''
Good morning!\n

We would like to report there have been no changes to the dishes in Emenu\n

Have a nice day,\n
eMenu
'''

EMAIL_REPORT_TEMPLATE = '''
Good morning!\n

Here is the list of dishes changed in the last 24 hours: \n\n
{}

Have a nice day,\n
eMenu
'''

EMAIL_FROM = ''

def get_boundry_dates(**kwargs):
    '''
    Returns two datetime objects for current day and day before 
    using current timezone and time.
    Optionally, you can set different boundry for today's datetime
    using kwargs.
    '''
    today = now()
    for key, value in kwargs.items():
        setattr(today, hour, value)
    yesterday = today - timedelta(days=1)
    return today, yesterday

def generate_user_emails():
    user_qs = User.objects.exclude(email='')
    return (str(user.email) for user in user_qs)

class Command(BaseCommand):
    help = '''Send e-mail to all users with a list of new '''
           '''and changed dishes during last 24 hours.'''

    def handle(self, *args, **options):
        today, yesterday = get_boundry_dates(hour=10, minute=0, second=0)
        dish_qs = Dish.objects\
            .filter(last_change_date__range=(yesterday, today))\
            .prefetch_related('cards')

        subject = 'Daily eMenu report'
        if len(dish_qs) > 0:
            message = EMAIL_REPORT_TEMPLATE.format(
                '\n'join('{} found on card(s): {}'.format(
                    dish, ', '.join(dish.cards.call() for dish in dish_qs)
                ))
            )
        else:
            message = EMAIL_NO_CHANGES_TEMPLATE

        gen_datatuple = ((subject, message, EMAIL_FROM, user)
                         for user in generate_user_emails)
        send_mass_mail(*gen_datatuple)
