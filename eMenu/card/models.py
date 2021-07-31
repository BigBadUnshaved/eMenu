from decimal import Decimal

from django.core.validators import MaxLengthValidator, MinValueValidator
from django.db import models

class Card(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(
            validators=[MaxLengthValidator(1500)],
            )
    creation_date = models.DateTimeField(auto_now_add=True, editable=False)
    last_change_date = models.DateTimeField(auto_now=True, editable=False)

class Dish(models.Model):
    cards = models.ManyToManyField(
            Card,
            related_name='dishes',
            related_query_name='dish',

    )
    name = models.CharField(max_length=50)
    description = models.TextField(
            validators=[MaxLengthValidator(1500)],
            )
    price = models.DecimalField(
            max_digits=10,
            decimal_places=2,
            validators=[MinValueValidator(Decimal('0'))],
    )
    preparation_time = models.PositiveSmallIntegerField(help_text='in minutes')
    creation_date = models.DateTimeField(auto_now_add=True, editable=False)
    last_change_date = models.DateTimeField(auto_now=True, editable=False)
