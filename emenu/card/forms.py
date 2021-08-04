from django import forms


class CardListForm(forms.Form):
    name = forms.CharField(required=False, max_length=50)
    creation_date__gte = forms.DateTimeField(
            required=False, label='creation date from')
    creation_date__lte = forms.DateTimeField(
            required=False, label='creation date to')
    last_change_date__gte = forms.DateTimeField(
            required=False, label='last change date from')
    last_change_date__lte = forms.DateTimeField(
            required=False, label='last change date to')
    order_choices = [
        ('', ''),
        ('name', 'by name (ascending)'),
        ('-name', 'by name (descending'),
        ('dishes_count', 'by number of dishes (ascending)'),
        ('-dishes_count', 'by number of dishes (descending)'),
    ]
    order_by = forms.ChoiceField(required=False, choices=order_choices)

