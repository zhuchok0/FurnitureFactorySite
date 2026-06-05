# main/tests/test_models.py
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from main.models import Type, Design, Furniture, Client, Position, Employee, Order, News, Term, Vacancy, PromoCode, Review

User = get_user_model()


class TypeModelTest(TestCase):
    def test_create_type(self):
        t = Type.objects.create(name='Kitchen')
        self.assertEqual(str(t), 'Kitchen')

    def test_unique_name(self):
        Type.objects.create(name='Office')
        with self.assertRaises(Exception):
            Type.objects.create(name='Office')

    def test_case_insensitive_unique(self):
        Type.objects.create(name='Loft')
        with self.assertRaises(ValidationError):
            t2 = Type(name='loft')
            t2.full_clean()


class DesignModelTest(TestCase):
    def test_create_design(self):
        d = Design.objects.create(name='Vanguard')
        self.assertEqual(str(d), 'Vanguard')

    def test_case_insensitive_unique(self):
        Design.objects.create(name='LOFT')
        with self.assertRaises(ValidationError):
            d2 = Design(name='loft')
            d2.full_clean()


class FurnitureModelTest(TestCase):
    def setUp(self):
        self.design = Design.objects.create(name='Modern')
        self.type1 = Type.objects.create(name='Chair')
        self.type2 = Type.objects.create(name='Table')

    def test_create_furniture(self):
        f = Furniture.objects.create(
            title='Comfort Chair',
            design=self.design,
            price=Decimal('199.99')
        )
        f.type.add(self.type1)
        self.assertEqual(str(f), 'Comfort Chair')
        self.assertEqual(f.price, Decimal('199.99'))
        self.assertFalse(f.in_production)

    def test_product_code_generation(self):
        f1 = Furniture.objects.create(
            title='Desk',
            design=self.design,
            price=Decimal('299.99')
        )
        # first furniture -> design prefix + "001"
        self.assertEqual(f1.product_code, 'MODE-001')

        f2 = Furniture.objects.create(
            title='Shelf',
            design=self.design,
            price=Decimal('89.99')
        )
        self.assertEqual(f2.product_code, 'MODE-002')

    def test_product_code_unique_and_not_editable(self):
        f = Furniture.objects.create(
            title='Lamp',
            design=self.design,
            price=Decimal('49.99')
        )
        # Попытка вручную изменить product_code игнорируется
        f.product_code = 'XXXX-999'
        f.save()
        f.refresh_from_db()
        self.assertNotEqual(f.product_code, 'XXXX-999')

    def test_many_to_many_types(self):
        f = Furniture.objects.create(
            title='Convertible',
            design=self.design,
            price=Decimal('399.99')
        )
        f.type.add(self.type1, self.type2)
        self.assertEqual(f.type.count(), 2)
        self.assertIn(self.type1, f.type.all())


class ClientModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='client1', password='testpass')

    def test_create_client(self):
        client = Client.objects.create(
            user=self.user,
            company_name='Best Office',
            responsible_person='John Doe',
            age=30,
            phone='+375 (29) 123-45-67',
            city='Minsk',
            address='Lenina 10',
            timezone='Europe/Minsk'
        )
        self.assertEqual(str(client), 'Best Office')
        self.assertEqual(client.age, 30)

    def test_age_validators(self):
        client = Client(
            user=self.user,
            company_name='Test',
            age=17,
            phone='+375 (29) 123-45-67',
            city='Minsk',
            address='Street',
            timezone='UTC'
        )
        with self.assertRaises(ValidationError):
            client.full_clean()

        client.age = 121
        with self.assertRaises(ValidationError):
            client.full_clean()

    def test_phone_validator(self):
        client = Client(
            user=self.user,
            company_name='Test',
            age=25,
            phone='12345',  # неверный формат
            city='Minsk',
            address='Street',
            timezone='UTC'
        )
        with self.assertRaises(ValidationError):
            client.full_clean()

    def test_timezone_update_tracking(self):
        client = Client.objects.create(
            user=self.user,
            company_name='Initial',
            age=25,
            phone='+375 (29) 123-45-67',
            city='Minsk',
            address='Street',
            timezone='UTC'
        )
        self.assertIsNone(client.timezone_updated_at)

        # Меняем часовой пояс
        client.timezone = 'Europe/Minsk'
        client.save()
        client.refresh_from_db()
        self.assertIsNotNone(client.timezone_updated_at)

        # Повторное сохранение без смены таймзоны не должно менять метку
        old_timestamp = client.timezone_updated_at
        client.company_name = 'Updated'
        client.save()
        client.refresh_from_db()
        self.assertEqual(client.timezone_updated_at, old_timestamp)


class PositionModelTest(TestCase):
    def test_create_position(self):
        pos = Position.objects.create(name='Manager', salary=Decimal('1500.00'))
        self.assertEqual(str(pos), 'Manager ($1500.00)')


class EmployeeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='emp1', password='testpass')
        self.position = Position.objects.create(name='Carpenter', salary=Decimal('1200.00'))

    def test_create_employee(self):
        emp = Employee.objects.create(
            user=self.user,
            first_name='Ivan',
            last_name='Petrov',
            age=30,
            phone='+375 (29) 111-22-33',
            email='ivan@example.com',
            position=self.position
        )
        self.assertEqual(emp.full_name, 'Petrov Ivan')
        self.assertEqual(str(emp), 'Petrov Ivan - Carpenter ($1200.00)')

    def test_email_unique(self):
        Employee.objects.create(
            user=self.user,
            first_name='A',
            last_name='B',
            age=25,
            phone='+375 (29) 000-00-00',
            email='dup@example.com',
            position=self.position
        )
        user2 = User.objects.create_user(username='emp2', password='testpass')
        with self.assertRaises(Exception):
            Employee.objects.create(
                user=user2,
                first_name='C',
                last_name='D',
                age=25,
                phone='+375 (29) 111-11-11',
                email='dup@example.com',
                position=self.position
            )

    def test_age_validators(self):
        emp = Employee(
            user=self.user,
            first_name='A',
            last_name='B',
            age=17,
            phone='+375 (29) 123-45-67',
            email='a@b.com',
            position=self.position
        )
        with self.assertRaises(ValidationError):
            emp.full_clean()

        emp.age = 66
        with self.assertRaises(ValidationError):
            emp.full_clean()


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cl', password='pass')
        self.client = Client.objects.create(
            user=self.user,
            company_name='ClientCo',
            age=30,
            phone='+375 (29) 123-45-67',
            city='Minsk',
            address='Addr',
            timezone='UTC'
        )
        self.design = Design.objects.create(name='Wood')
        self.furniture = Furniture.objects.create(
            title='Table',
            design=self.design,
            price=Decimal('500.00')
        )

    def test_create_order(self):
        order = Order.objects.create(
            client=self.client,
            furniture=self.furniture,
            quantity=2,
            order_date=date.today(),
            delivery_date=date.today() + timedelta(days=10)
        )
        self.assertEqual(order.total_price, Decimal('1000.00'))
        self.assertIn('Order #', str(order))

    def test_quantity_validation(self):
        order = Order(
            client=self.client,
            furniture=self.furniture,
            quantity=0,
            order_date=date.today()
        )
        with self.assertRaises(ValidationError):
            order.full_clean()


class PromoCodeModelTest(TestCase):
    def test_is_expired(self):
        today = date.today()
        promo = PromoCode.objects.create(
            code='OLD',
            discount=Decimal('10.00'),
            description='Expired',
            valid_from=today - timedelta(days=10),
            valid_to=today - timedelta(days=1)
        )
        self.assertTrue(promo.is_expired)
        self.assertFalse(promo.is_upcoming)

    def test_is_upcoming(self):
        today = date.today()
        promo = PromoCode.objects.create(
            code='FUTURE',
            discount=Decimal('15.00'),
            description='Future',
            valid_from=today + timedelta(days=1),
            valid_to=today + timedelta(days=10)
        )
        self.assertTrue(promo.is_upcoming)
        self.assertFalse(promo.is_expired)

    def test_active_promo(self):
        today = date.today()
        promo = PromoCode.objects.create(
            code='NOW',
            discount=Decimal('20.00'),
            description='Active',
            valid_from=today - timedelta(days=1),
            valid_to=today + timedelta(days=1)
        )
        self.assertFalse(promo.is_expired)
        self.assertFalse(promo.is_upcoming)


class ReviewModelTest(TestCase):
    def test_create_review(self):
        r = Review.objects.create(name='Alice', text='Great!', rating=5)
        self.assertEqual(str(r), 'Alice: 5 stars')

    def test_rating_validator(self):
        r = Review(name='Bob', text='Bad', rating=0)
        with self.assertRaises(ValidationError):
            r.full_clean()
        r.rating = 6
        with self.assertRaises(ValidationError):
            r.full_clean()


# Простые тесты для News, Term, Vacancy – создание и строковое представление
class SimpleModelsTest(TestCase):
    def test_news(self):
        n = News.objects.create(title='New Collection', short_content='...')
        self.assertEqual(str(n), 'New Collection')

    def test_term(self):
        t = Term.objects.create(question='What is MDF?', answer='Medium Density Fibreboard')
        self.assertEqual(str(t), 'What is MDF?')

    def test_vacancy(self):
        v = Vacancy.objects.create(
            title='Designer',
            description='Design furniture',
            salary=Decimal('2000.00'),
            location='Minsk'
        )
        self.assertEqual(str(v), 'Designer')
        self.assertTrue(v.is_active)
