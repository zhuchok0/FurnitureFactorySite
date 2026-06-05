from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from datetime import date
from django.urls import reverse
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.conf import settings
import pytz
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class Type(models.Model):
    name = models.CharField(max_length=30, 
                            help_text="Enter a furniture type(e.g. Kitchen, Office, Cabinet etc.)",
                            unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='type_name_case_insensitive_unique',
                violation_error_message = "Type already exists (case insensitive match)"
            ),
        ]
    

class Design(models.Model):
    name = models.CharField(max_length=30,
                            help_text="Enter a furniture design(e.g. Loft, Vanguard)",
                            unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='design_name_case_insensitive_unique',
                violation_error_message = "Design already exists (case insensitive match)"
            ),
        ]
    

class Furniture(models.Model):
    title = models.CharField(max_length=100)
    type = models.ManyToManyField(Type, help_text="Choose a type for this furniture")
    design = models.ForeignKey('Design', on_delete=models.RESTRICT, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    in_production = models.BooleanField(default=False,
                                        verbose_name='In production')
    
    product_code = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        blank=True,
        verbose_name="Product Code"
    )
    
    def save(self, *args, **kwargs):
        if self.pk is None:
            if not self.product_code and self.design:
                design_prefix = self.design.name[:4].upper()
                furniture_count = Furniture.objects.count() + 1
                self.product_code = f"{design_prefix}-{furniture_count:03d}"
                logger.info(f'Generated product code {self.product_code} for new furniture "{self.title}"')
        else:
            old_code = Furniture.objects.get(pk=self.pk).product_code
            self.product_code = old_code

        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']


class Client(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        related_name='client_profile',
        verbose_name="User account"
    )
    company_name = models.CharField(
        max_length=100,
        default="Default",
        help_text="Full company name"
    )
    responsible_person = models.CharField(
        max_length=100,
        verbose_name="Responsible Person",
        help_text="Full name of the responsible contact person",
        default='',
        blank=True 
    )
    age = models.PositiveIntegerField(
        validators=[
            MinValueValidator(18, message="Client must be at least 18 years old"),
            MaxValueValidator(120, message="Invalid age")
        ],
        help_text="Client's age (must be 18 or older)", 
        blank=True,
        null=True
    )
    phone = models.CharField(
    max_length=20,
    validators=[
        RegexValidator(
            regex=r'^\+375 \(29\) \d{3}-\d{2}-\d{2}$',
            message="Enter a valid phone number (e.g., +375 (29) 123-45-67)"
        )
    ],
    help_text="Enter phone number (e.g., +375 (29) 123-45-67)"
    )
    city = models.CharField(
        max_length=50,
        help_text="City of residence/office"
    )
    address = models.TextField(
        help_text="Full street address"
    )
    timezone = models.CharField(
        max_length=50,
        choices=[(tz, tz) for tz in pytz.common_timezones], 
        default='UTC',
        help_text="Select your timezone"
    )
    timezone_updated_at = models.DateTimeField(null=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)
            return

        old_timezone = Client.objects.filter(pk=self.pk).values_list('timezone', flat=True).first()
        if old_timezone != self.timezone:
            self.timezone_updated_at = timezone.now() 
            logger.info(f'Client "{self.company_name}" changed timezone from {old_timezone} to {self.timezone}')
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.company_name
    
    class Meta:
        ordering = ['company_name']


class Position(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Enter job position (e.g., Director, SMM, Manager, Storekeeper, Carpenter)"
    )
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Monthly salary in currency units"
    )
    
    def __str__(self):
        return f"{self.name} (${self.salary})"
    
    class Meta:
        ordering = ['name']


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        related_name='employee_profile',
        verbose_name="User account",
        help_text="Link to user account for authentication"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(
        validators=[
            MinValueValidator(18, message="Employee must be at least 18 years old"),
            MaxValueValidator(65, message="Employee must be under 65 years old")
        ],
        help_text="Employee's age (18-65)"
    )
    photo = models.ImageField(
        upload_to='employees/',
        null=True,
        blank=True,
        help_text="Employee photo (optional)"
    )
    phone = models.CharField(
    max_length=20,
    validators=[
        RegexValidator(
            regex=r'^\+375 \(29\) \d{3}-\d{2}-\d{2}$',
            message="Enter a valid phone number (e.g., +375 (29) 123-45-67)"
        )
    ],
    help_text="Enter phone number (e.g., +375 (29) 123-45-67)"
    )
    email = models.EmailField(unique=True)

    position = models.ForeignKey(
        'Position',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Select employee's position"
    )
    
    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"
    
    def __str__(self):
        return f"{self.full_name} - {self.position}"
    
    class Meta:
        ordering = ['last_name', 'first_name']


class Order(models.Model):
    client = models.ForeignKey(
        'Client',
        on_delete=models.PROTECT, 
    )
    furniture = models.ForeignKey(
        'Furniture',
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    order_date = models.DateField(
        default=date.today,
        help_text="Date when order was placed"
    )
    delivery_date = models.DateField(
        help_text="Expected delivery date",
        null=True,
        blank=True
    )
    
    @property
    def total_price(self):
        return self.furniture.price * self.quantity
    
    def __str__(self):
        return f"Order #{self.id} - {self.client.company_name} - {self.furniture.title} ({self.quantity} pcs)"
    
    class Meta:
        ordering = ['-order_date']


class News(models.Model):
    title = models.CharField(
        max_length=200,
        help_text="News headline"
    )
    short_content = models.CharField(
        max_length=300,
        help_text="One sentence summary (max 300 characters)"
    )
    image = models.ImageField(
        upload_to='news_images/',
        help_text="News image (optional)"
    )
    created_date = models.DateField(auto_now_add=True,)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_date']
        verbose_name_plural = "News"


class Term(models.Model):
    question = models.CharField(
        max_length=300,
        help_text="Enter the term or question"
    )
    answer = models.TextField(
        help_text="Enter the explanation or answer"
    )
    
    def __str__(self):
        return self.question
    
    class Meta:
        ordering = ['question']


class Vacancy(models.Model):
    title = models.CharField(
        max_length=200,
        help_text="Job title (e.g., Furniture Designer, Sales Manager)"
    )
    description = models.TextField(
        help_text="Full job description, requirements, and responsibilities"
    )
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Monthly salary in currency units (e.g., 1500.00)"
    )
    location = models.CharField(
        max_length=100,
        default="Minsk, Belarus",
        help_text="Work location"
    )
    created_date = models.DateField(
        auto_now_add=True,
        help_text="Date when vacancy was posted"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Show this vacancy on the website"
    )
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_date']
        verbose_name_plural = "Vacancies"


class PromoCode(models.Model):
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Promo code (e.g., SUMMER2024, DISCOUNT10)"
    )
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Discount amount (e.g., 10.00 for 10%)"
    )
    description = models.CharField(
        max_length=200,
        help_text="Brief description of the promo"
    )
    valid_from = models.DateField(
        help_text="Date when promo code becomes valid"
    )
    valid_to = models.DateField(
        help_text="Date when promo code expires"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this promo code currently active?"
    )
    created_date = models.DateField(
        auto_now_add=True,
        help_text="Date when promo was created"
    )
    
    @property
    def is_expired(self):
        from datetime import date
        return date.today() > self.valid_to
    
    @property
    def is_upcoming(self):
        from datetime import date
        return date.today() < self.valid_from
    
    def __str__(self):
        return f"{self.code} - {self.discount}%"
    
    class Meta:
        ordering = ['valid_from', 'code']
        verbose_name = "Promo Code"
        verbose_name_plural = "Promo Codes"

class Review(models.Model):
    name = models.CharField(max_length=100, verbose_name="Your name")
    text = models.TextField(verbose_name="Review text")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Rating (1-5)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created")

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Reviews"

    def __str__(self):
        return f"{self.name}: {self.rating} stars"
