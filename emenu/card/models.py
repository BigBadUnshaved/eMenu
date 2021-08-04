from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

def assert_text_field_length(obj, field_name='description'):
    '''
    Checks if for the given object the value assigned to the provided 
    text field (description on default) complies with it's max_length. 
    '''
    obj_class = obj.__class__
    deff_attribute = getattr(obj_class, field_name)
    max_length = deff_attribute.field.max_length
    field_value = getattr(obj, field_name)
    value_len = len(field_value)
    try:
        assert value_len <= max_length
    except AssertionError:
        message = 'Length of {} cannot exceed {} characters (current: {})'
        message = message.format(field_name, max_length, value_len)
        raise ValidationError(message)

class EmenuModel(models.Model):
    '''
    Abstract model that contains common code for both Card and Dish models
    '''
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(
            blank=True,
            max_length=1500,
            )
    creation_date = models.DateTimeField(auto_now_add=True, editable=False)
    last_change_date = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        class_name = self.__class__.__name__.lower()
        return reverse('{}-detail'.format(class_name), kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        assert_text_field_length(self)
        super().save(*args, **kwargs)


class Card(EmenuModel):
    '''
    Model that corresponds to a single menu card.
    '''
    pass

class Dish(EmenuModel):
    '''
    Model that corresponds to a single dish.
    '''
    cards = models.ManyToManyField(
            Card,
            blank=True,
            related_name='dishes',
            related_query_name='dishes',

    )
    price = models.DecimalField(
            max_digits=10,
            decimal_places=2,
            validators=[MinValueValidator(Decimal('0'))],
            help_text='in PLN',
    )
    preparation_time = models.PositiveSmallIntegerField(help_text='in minutes')
    is_vegetarian = models.BooleanField(
            verbose_name='vegetarian',
            default=False,
    )

    class Meta:
        verbose_name_plural = 'dishes'

    def save(self, *args, **kwargs):
        try:
            assert self.price >= Decimal(0)
        except AssertionError:
            msg = 'Price cannot be lower then 0.00'
            raise ValidationError(msg)
        super().save(*args, **kwargs)

