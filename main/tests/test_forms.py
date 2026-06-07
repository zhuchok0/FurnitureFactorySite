from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from main.forms import OrderForm, ReviewForm, ClientRegistrationForm
from main.models import Type, Design, Furniture, Client, Order, Review

from dateutil.relativedelta import relativedelta

User = get_user_model()


class OrderFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.design = Design.objects.create(name='Modern')
        cls.type1 = Type.objects.create(name='Chair')
        cls.type2 = Type.objects.create(name='Table')
        cls.furniture_in_prod = Furniture.objects.create(
            title='Available Chair',
            design=cls.design,
            price=Decimal('100.00'),
            in_production=True
        )
        cls.furniture_in_prod.type.add(cls.type1)
        cls.furniture_not_in_prod = Furniture.objects.create(
            title='Unavailable Table',
            design=cls.design,
            price=Decimal('200.00'),
            in_production=False
        )
        cls.furniture_not_in_prod.type.add(cls.type2)

    def test_valid_order(self):
        data = {
            'furniture': self.furniture_in_prod.id,
            'quantity': 2,
            'delivery_date': date.today() + self._months(3),
        }
        form = OrderForm(data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_furniture_not_in_production(self):
        form = OrderForm()
        self.assertNotIn(self.furniture_not_in_prod.id,
                         form.fields['furniture'].queryset.values_list('id', flat=True))
        data = {
            'furniture': self.furniture_not_in_prod.id,
            'quantity': 1,
            'delivery_date': date.today() + self._months(3),
        }
        form = OrderForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('furniture', form.errors)

    def test_quantity_min_value(self):
        data = {
            'furniture': self.furniture_in_prod.id,
            'quantity': 0,
            'delivery_date': date.today() + self._months(3),
        }
        form = OrderForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)

    def test_delivery_date_too_early(self):
        data = {
            'furniture': self.furniture_in_prod.id,
            'quantity': 1,
            'delivery_date': date.today() + self._months(2),
        }
        form = OrderForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_date', form.errors)
        self.assertIn('at least 3 months', form.errors['delivery_date'][0])

    def test_delivery_date_exactly_3_months(self):
        data = {
            'furniture': self.furniture_in_prod.id,
            'quantity': 1,
            'delivery_date': date.today() + self._months(3),
        }
        form = OrderForm(data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_delivery_date_optional(self):
        data = {
            'furniture': self.furniture_in_prod.id,
            'quantity': 3,
        }
        form = OrderForm(data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.cleaned_data['delivery_date'])

    @staticmethod
    def _months(n):
        from dateutil.relativedelta import relativedelta
        return relativedelta(months=n)


class ReviewFormTest(TestCase):
    def test_valid_review(self):
        data = {'name': 'Alice', 'text': 'Great product!', 'rating': 5}
        form = ReviewForm(data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_rating_below_1(self):
        data = {'name': 'Bob', 'text': 'Bad', 'rating': 0}
        form = ReviewForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)

    def test_invalid_rating_above_5(self):
        data = {'name': 'Bob', 'text': 'Super', 'rating': 6}
        form = ReviewForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)

    def test_required_fields(self):
        form = ReviewForm({})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('text', form.errors)
        self.assertIn('rating', form.errors)

    def test_widget_choices(self):
        form = ReviewForm()
        choices = dict(form.fields['rating'].widget.choices)
        self.assertEqual(choices[1], '1 star')
        self.assertEqual(choices[5], '5 stars')


class ClientRegistrationFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Group.objects.get_or_create(name='Client')

    def test_valid_registration(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'company_name': 'Test Company',
            'phone': '+375 (29) 123-45-67',
            'city': 'Minsk',
            'address': 'Some street, 1',
            'date_of_birth': (date.today() - relativedelta(years=20)).isoformat(),  # 20 лет назад
            'timezone': 'Europe/Minsk',
            'responsible_person': 'John Doe',
        }
        form = ClientRegistrationForm(data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_required_fields(self):
        form = ClientRegistrationForm({})
        required = ['username', 'email', 'password1', 'password2',
                    'company_name', 'phone', 'city', 'address', 'date_of_birth', 'timezone']
        self.assertFalse(form.is_valid())
        for field in required:
            self.assertIn(field, form.errors, f"Missing error for {field}")

    def test_email_validation(self):
        data = {
            'username': 'test',
            'email': 'notanemail',
            'password1': 'ComplexPass1!',
            'password2': 'ComplexPass1!',
            'company_name': 'Test',
            'phone': '+375 (29) 123-45-67',
            'city': 'Minsk',
            'address': 'Addr',
            'date_of_birth': (date.today() - relativedelta(years=20)).isoformat(),
            'timezone': 'UTC',
        }
        form = ClientRegistrationForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_password_mismatch(self):
        data = {
            'username': 'user',
            'email': 'user@example.com',
            'password1': 'StrongPass1!',
            'password2': 'DifferentPass2!',
            'company_name': 'Test',
            'phone': '+375 (29) 123-45-67',
            'city': 'Minsk',
            'address': 'Addr',
            'date_of_birth': (date.today() - relativedelta(years=20)).isoformat(),
            'timezone': 'UTC',
        }
        form = ClientRegistrationForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_phone_format_validation(self):
        data = {
            'username': 'user',
            'email': 'user@example.com',
            'password1': 'StrongPass1!',
            'password2': 'StrongPass1!',
            'company_name': 'Test',
            'phone': '1234567',  
            'city': 'Minsk',
            'address': 'Addr',
            'date_of_birth': (date.today() - relativedelta(years=20)).isoformat(),
            'timezone': 'UTC',
        }
        form = ClientRegistrationForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_date_of_birth_validation_min_age(self):
        today = date.today()
        dob_17 = today - relativedelta(years=17)
        data = {
            'username': 'younguser',
            'email': 'young@example.com',
            'password1': 'StrongPass1!',
            'password2': 'StrongPass1!',
            'company_name': 'Young Co',
            'phone': '+375 (29) 123-45-67',
            'city': 'Minsk',
            'address': 'Addr',
            'date_of_birth': dob_17.isoformat(),
            'timezone': 'UTC',
        }
        form = ClientRegistrationForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_of_birth', form.errors)
        self.assertIn('at least 18 years old', form.errors['date_of_birth'][0])

        dob_exactly_18 = today - relativedelta(years=18)
        data['date_of_birth'] = dob_exactly_18.isoformat()
        form = ClientRegistrationForm(data)
        self.assertTrue(form.is_valid(), form.errors)

        dob_19 = today - relativedelta(years=19)
        data['date_of_birth'] = dob_19.isoformat()
        form = ClientRegistrationForm(data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_save_creates_user_and_client(self):
        today = date.today()
        dob = today - relativedelta(years=30) 
        data = {
            'username': 'savetest',
            'email': 'save@example.com',
            'password1': 'SecureP@ssw0rd!',
            'password2': 'SecureP@ssw0rd!',
            'company_name': 'SaveCorp',
            'phone': '+375 (29) 777-77-77',
            'city': 'Minsk',
            'address': 'Test address',
            'date_of_birth': dob.isoformat(),
            'timezone': 'Europe/Minsk',
            'responsible_person': 'Ivan Ivanov',
        }
        form = ClientRegistrationForm(data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertIsNotNone(user.pk)
        self.assertTrue(user.check_password('SecureP@ssw0rd!'))
        self.assertEqual(user.email, 'save@example.com')
        self.assertTrue(user.groups.filter(name='Client').exists())

        client = Client.objects.get(user=user)
        self.assertEqual(client.company_name, 'SaveCorp')
        self.assertEqual(client.phone, '+375 (29) 777-77-77')
        self.assertEqual(client.date_of_birth, dob)
        self.assertEqual(client.age, 30)
        self.assertEqual(client.timezone, 'Europe/Minsk')
        self.assertEqual(client.responsible_person, 'Ivan Ivanov')
