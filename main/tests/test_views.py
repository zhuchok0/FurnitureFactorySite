import io
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, Client as TestClient
from django.urls import reverse

from main.models import (
    Type, Design, Furniture, Client, Position, Employee,
    Order, News, Vacancy, PromoCode, Review
)

User = get_user_model()


class ViewsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        import matplotlib
        matplotlib.use('Agg')

    def setUp(self):
        self.client = TestClient()

        self.client_group = Group.objects.create(name='Client')
        self.employee_group = Group.objects.create(name='Employee')

        self.admin_user = User.objects.create_superuser(username='admin', password='adminpass')
        self.client_user = User.objects.create_user(username='clientuser', password='clientpass')
        self.employee_user = User.objects.create_user(username='employeeuser', password='employeepass')
        self.plain_user = User.objects.create_user(username='plainuser', password='plainpass')

        self.client_user.groups.add(self.client_group)
        self.employee_user.groups.add(self.employee_group)

        today = date.today()
        dob_client = today - relativedelta(years=30)
        self.client_profile = Client.objects.create(
            user=self.client_user,
            company_name='TestClient Ltd',
            responsible_person='John Doe',
            date_of_birth=dob_client,
            phone='+375 (29) 123-45-67',
            city='Minsk',
            address='Lenina 1',
            timezone='Europe/Minsk'
        )

        self.position = Position.objects.create(name='Manager', salary=Decimal('1500.00'))
        dob_employee = today - relativedelta(years=25)
        self.employee = Employee.objects.create(
            user=self.employee_user,
            first_name='Ivan',
            last_name='Petrov',
            date_of_birth=dob_employee,
            phone='+375 (29) 987-65-43',
            email='ivan@test.com',
            position=self.position
        )

        self.type1 = Type.objects.create(name='Kitchen')
        self.type2 = Type.objects.create(name='Office')
        self.design1 = Design.objects.create(name='Modern')
        self.design2 = Design.objects.create(name='Loft')

        self.furniture1 = Furniture.objects.create(
            title='Table',
            design=self.design1,
            price=Decimal('200.00'),
            in_production=True     
        )
        self.furniture1.type.add(self.type1)

        self.furniture2 = Furniture.objects.create(
            title='Chair',
            design=self.design2,
            price=Decimal('50.00'),
            in_production=True         
        )
        self.furniture2.type.add(self.type2)

        self.order1 = Order.objects.create(
            client=self.client_profile,
            furniture=self.furniture1,
            quantity=2,
            order_date=date.today(),
            delivery_date=date.today() + timedelta(days=5)
        )

        self.order2 = Order.objects.create(
            client=self.client_profile,
            furniture=self.furniture2,
            quantity=3,
            order_date=date.today() - timedelta(days=10),
            delivery_date=date.today() - timedelta(days=5)
        )

        self.news = News.objects.create(title='Breaking News', short_content='...')
        self.vacancy = Vacancy.objects.create(
            title='Designer',
            description='Design furniture',
            salary=Decimal('1200.00'),
            location='Minsk'
        )
        self.promo_active = PromoCode.objects.create(
            code='HOT20',
            discount=Decimal('20.00'),
            description='20% off',
            valid_from=date.today() - timedelta(days=1),
            valid_to=date.today() + timedelta(days=10),
            is_active=True
        )
        self.promo_expired = PromoCode.objects.create(
            code='OLD10',
            discount=Decimal('10.00'),
            description='Expired',
            valid_from=date.today() - timedelta(days=20),
            valid_to=date.today() - timedelta(days=5),
            is_active=True
        )
        self.review = Review.objects.create(name='Alice', text='Great!', rating=5)

    def test_main_page_anonymous(self):
        response = self.client.get(reverse('main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main.html')
        
        self.assertIn('latest_news', response.context)
        self.assertIn('clients', response.context)
        self.assertIn('total_sales', response.context)

    @patch('main.views.requests.get')
    def test_main_page_authenticated_client_weather_and_video_mocked(self, mock_get):
        mock_weather_response = MagicMock()
        mock_weather_response.json.return_value = {
            'cod': 200,
            'name': 'Minsk',
            'main': {'temp': 15.0},
            'weather': [{'icon': '01d', 'description': 'clear sky'}]
        }
        mock_weather_response.raise_for_status = MagicMock()

        mock_video_response = MagicMock()
        mock_video_response.json.return_value = {
            'items': [{
                'id': 'qlpE7SFtMPQ',
                'snippet': {'title': 'Test Video'}
            }]
        }
        mock_video_response.raise_for_status = MagicMock()

        mock_get.side_effect = [mock_weather_response, mock_video_response]

        self.client.login(username='clientuser', password='clientpass')
        response = self.client.get(reverse('main'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['client_info'])
        self.assertIsNotNone(response.context['client_info']['calendar'])
        self.assertIsNotNone(response.context['weather_info'])
        self.assertEqual(response.context['weather_info']['city'], 'Minsk')
        self.assertIsNotNone(response.context['video_data'])
        self.assertEqual(response.context['video_data']['title'], 'Test Video')

    def test_news_list(self):
        response = self.client.get(reverse('news_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news_list.html')
        self.assertContains(response, self.news.title)

    def test_about(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about.html')

    def test_contacts(self):
        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contacts.html')
        self.assertContains(response, 'Ivan')

    def test_privacy_policy(self):
        response = self.client.get(reverse('privacy_policy'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'privacy_policy.html')

    def test_vacancies_list(self):
        response = self.client.get(reverse('vacancies_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vacancies_list.html')
        self.assertEqual(len(response.context['vacancies']), 1)
        self.assertTrue(response.context['vacancies'][0].is_active)

    def test_promocodes_list(self):
        response = self.client.get(reverse('promocodes_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promocodes_list.html')
       
        self.assertEqual(len(response.context['active_promocodes']), 1)
        self.assertEqual(response.context['active_promocodes'][0].code, 'HOT20')
        
        self.assertEqual(len(response.context['archive_promocodes']), 1)
        self.assertEqual(response.context['archive_promocodes'][0].code, 'OLD10')

    def test_reviews_list(self):
        response = self.client.get(reverse('reviews_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reviews.html')
        self.assertContains(response, 'Alice')

    def test_catalog_default_sort(self):
        response = self.client.get(reverse('catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog.html')
        furniture_list = list(response.context['furniture_list'])
        
        self.assertEqual(furniture_list[0].title, 'Chair')
        self.assertEqual(furniture_list[1].title, 'Table')

    def test_catalog_sort_desc(self):
        response = self.client.get(reverse('catalog'), {'sort': 'price_desc'})
        furniture_list = list(response.context['furniture_list'])
        self.assertEqual(furniture_list[0].title, 'Table')

    # authentacation

    def test_register_client_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register_client.html')

    def test_register_client_post_valid(self):
        today = date.today()
        dob = (today - relativedelta(years=25)).isoformat()
        data = {
            'username': 'newclient',
            'email': 'newclient@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'company_name': 'New Corp',
            'responsible_person': 'John Smith',
            'date_of_birth': dob, 
            'phone': '+375 (29) 555-55-55',
            'city': 'Minsk',
            'address': 'Main Street',
            'timezone': 'Europe/Minsk',
        }
        response = self.client.post(reverse('register'), data)  
        self.assertRedirects(response, reverse('main'))
        
        user = User.objects.get(username='newclient')
        self.assertTrue(user.groups.filter(name='Client').exists())
        self.assertTrue(Client.objects.filter(user=user).exists())

    def test_add_review_requires_login(self):
        response = self.client.get(reverse('add_review'))
        self.assertNotEqual(response.status_code, 200)  
        self.assertIn('/accounts/login/', response.url)

    def test_add_review_post(self):
        self.client.login(username='clientuser', password='clientpass')
        response = self.client.post(reverse('add_review'), {
            'name': 'Bob',
            'text': 'Nice!',
            'rating': 4
        })
        self.assertRedirects(response, reverse('reviews_list'))
        self.assertTrue(Review.objects.filter(name='Bob').exists())

    # client pages-

    def test_client_orders_requires_client_group(self):
        self.client.login(username='plainuser', password='plainpass')
        response = self.client.get(reverse('client_orders'))
        self.assertNotEqual(response.status_code, 200)

    def test_client_orders_as_client(self):
        self.client.login(username='clientuser', password='clientpass')
        response = self.client.get(reverse('client_orders'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client_orders.html')
        orders = response.context['orders']
        self.assertEqual(len(orders), 2)

    def test_create_order_get(self):
        self.client.login(username='clientuser', password='clientpass')
        response = self.client.get(reverse('create_order'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'order_form.html')

    def test_create_order_post(self):
        self.client.login(username='clientuser', password='clientpass')
        future_delivery = date.today() + relativedelta(months=3)
        response = self.client.post(reverse('create_order'), {
            'furniture': self.furniture1.id,
            'quantity': 1,
            'delivery_date': future_delivery
        })
        self.assertRedirects(response, reverse('client_orders'))
        self.assertEqual(Order.objects.count(), 3)
        new_order = Order.objects.last()
        self.assertEqual(new_order.client, self.client_profile)

    # employee pages

    def test_employee_dashboard_requires_employee_group(self):
        self.client.login(username='plainuser', password='plainpass')
        response = self.client.get(reverse('employee_dashboard'))
        self.assertNotEqual(response.status_code, 200)

    def test_employee_dashboard_as_employee(self):
        self.client.login(username='employeeuser', password='employeepass')
        response = self.client.get(reverse('employee_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee_dashboard.html')
        self.assertIn('clients', response.context)
        self.assertIn('orders', response.context)

    # admin pages

    def test_analytics_dashboard_admin_access(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('analytics_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics_dashboard.html')
        
        self.assertIn('price_list', response.context)
        self.assertIn('yearly_stats', response.context)

    def test_analytics_dashboard_redirect_for_non_admin(self):
        self.client.login(username='clientuser', password='clientpass')
        response = self.client.get(reverse('analytics_dashboard'))
        self.assertNotEqual(response.status_code, 200)

    def test_edit_review_admin(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('edit_review', args=[self.review.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_review.html')

        response = self.client.post(reverse('edit_review', args=[self.review.pk]), {
            'name': 'Alice Updated',
            'text': 'Even better!',
            'rating': 5
        })
        self.assertRedirects(response, reverse('reviews_list'))
        self.review.refresh_from_db()
        self.assertEqual(self.review.name, 'Alice Updated')

    def test_delete_review_admin(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('delete_review', args=[self.review.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'confirm_delete_review.html')

        response = self.client.post(reverse('delete_review', args=[self.review.pk]))
        self.assertRedirects(response, reverse('reviews_list'))
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())