from django import forms
from .models import Order, Furniture, Review, Client
from datetime import date
from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import pytz
from django.core.validators import RegexValidator
import logging

logger = logging.getLogger(__name__)

class OrderForm(forms.ModelForm):
    furniture = forms.ModelChoiceField(
        queryset=Furniture.objects.filter(in_production=True),
        empty_label="Select furniture",
        label="Furniture"
    )
    quantity = forms.IntegerField(min_value=1, initial=1, label="Quantity")
    delivery_date = forms.DateField(
        widget=forms.SelectDateWidget,
        required=False,
        label="Desired delivery date"
    )

    class Meta:
        model = Order
        fields = ['furniture', 'quantity', 'delivery_date']

    def clean_delivery_date(self):
        delivery_date = self.cleaned_data.get('delivery_date')
        if delivery_date:
            min_date = date.today() + relativedelta(months=3)
            if delivery_date < min_date:
                logger.warning(f'Order validation: delivery date {delivery_date} is earlier than minimum {min_date}')
                raise ValidationError(f'Delivery date must be at least 3 months from today (earliest: {min_date}).')
        return delivery_date
 
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'text', 'rating']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your name',
                'required': True,
                'minlength': 2,
                'title': 'Name must be at least 2 characters'
            }),
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Your feedback...',
                'required': True,
                'minlength': 10,
                'title': 'Review must be at least 10 characters'
            }),
            'rating': forms.Select(attrs={
                'required': True
            }, choices=[(i, f"{i} star{'s' if i > 1 else ''}") for i in range(1, 6)]),
        }

def validate_min_age(value):
    today = date.today()
    min_birth_date = today - relativedelta(years=18)
    if value > min_birth_date:
        raise ValidationError('You must be at least 18 years old.')

class ClientRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'required': True})
    )
    company_name = forms.CharField(
        max_length=100,
        label='Company name',
        widget=forms.TextInput(attrs={'required': True})
    )
    phone = forms.CharField(
        max_length=20,
        label='Phone number',
        help_text='Format: +375 (29) 123-45-67',
        validators=[RegexValidator(...)],  # серверная
        widget=forms.TextInput(attrs={
            'required': True,
            'pattern': r'^\+375 \(29\) \d{3}-\d{2}-\d{2}$',
            'title': 'Enter a valid phone number (e.g., +375 (29) 123-45-67)'
        })
    )
    city = forms.CharField(
        max_length=50,
        label='City',
        widget=forms.TextInput(attrs={'required': True})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'required': True}),
        label='Address'
    )
    responsible_person = forms.CharField(
        max_length=100,
        required=False,
        label='Responsible person',
        widget=forms.TextInput(attrs={'required': False})
    )
    date_of_birth = forms.DateField(
        label='Date of birth',
        help_text='You must be at least 18 years old.',
        validators=[validate_min_age],
        widget=forms.DateInput(attrs={
            'type': 'date',
            'required': True,
            'max': (date.today() - relativedelta(years=18)).isoformat()  # максимальная дата (18 лет назад)
        })
    )
    timezone = forms.ChoiceField(
        choices=[(tz, tz) for tz in pytz.common_timezones],
        initial='UTC',
        label='Timezone',
        help_text='Select your time zone',
        widget=forms.Select(attrs={'required': True})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        client = Client(
            user=user,
            company_name=self.cleaned_data['company_name'],
            phone=self.cleaned_data['phone'],
            city=self.cleaned_data['city'],
            address=self.cleaned_data['address'],
            responsible_person=self.cleaned_data.get('responsible_person', ''),
            date_of_birth=self.cleaned_data['date_of_birth'],
            timezone=self.cleaned_data['timezone'],  
        )
        if commit:
            client.save()
            from django.contrib.auth.models import Group
            group, _ = Group.objects.get_or_create(name='Client')
            user.groups.add(group)
            logger.info(f'New client registered: {user.username} ({client.company_name})')
        return user
