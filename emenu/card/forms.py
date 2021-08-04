from django import forms


class CardListForm(forms.Form):
    '''
    Form_class for cardlist using django generic views
    '''
    name = forms.CharField(required=False, max_length=50, strip=False)
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
        ('alph_name', 'alphabetically by name (ascending)'),
        ('-alph_name', 'alphabetically by name (descending'),
        ('dishes_count', 'by number of dishes (ascending)'),
        ('-dishes_count', 'by number of dishes (descending)'),
    ]
    order_by = forms.ChoiceField(required=False, choices=order_choices)

