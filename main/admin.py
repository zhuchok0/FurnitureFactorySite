from django.contrib import admin
from .models import Type, Design, Furniture, Position, Employee, Client, Order, News, Vacancy, PromoCode, CompanyInfo, FAQ, Partner

admin.site.register(Type)
admin.site.register(News)

class FurnitureInline(admin.TabularInline):
    model = Furniture
    extra = 1
    fields = ('title', 'price', 'in_production')
    show_change_link = True


@admin.register(Design)
class DesignAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [FurnitureInline]

@admin.register(Furniture)
class FurnitureAdmin(admin.ModelAdmin):
    list_display=('title', 'product_code', 'price', 'in_production')
    list_filter=('price', 'in_production')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display=('company_name', 'responsible_person', 'phone', 'city', 'address', 'user')
    list_filter=('city',)

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'salary')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display=('first_name', 'last_name', 'position', 'email', 'phone', 'user')
    list_filter=('position',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display=('id', 'furniture', 'quantity', 'delivery_date', 'client', 'total_price')
    list_filter=('order_date',)
    readonly_fields = ('total_price',)
    
    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'Total Price'

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'salary', 'location', 'created_date', 'is_active')
    list_filter = ('is_active', 'location')

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'description', 'valid_from', 'valid_to', 'is_active', 'is_expired')
    list_filter = ('is_active', 'valid_from', 'valid_to')
    search_fields = ('code', 'description')
    list_editable = ('is_active',)
    readonly_fields = ('created_date',)
    
    fieldsets = (
        ('Promo Code Information', {
            'fields': ('code', 'discount', 'description')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_to')
        }),
        ('Status', {
            'fields': ('is_active', 'created_date')
        }),
    )

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Main', {
            'fields': ('name', 'founded_year', 'description', 'mission')
        }),
        ('Logo & Video', {
            'fields': ('logo', 'video_file', 'video_title')
        }),
        ('Values (JSON format)', {
            'fields': ('values',),
            'description': 'Example: [{"title": "Quality", "description": "..."}]'
        }),
        ('History', {
            'fields': ('history',)
        }),
        ('Products', {
            'fields': ('products_info',)
        }),
        ('Requisites', {
            'fields': ('requisites',)
        }),
        ('Certificates', {
            'fields': ('certificates', 'certificate_image')
        }),
        ('Contact & Hours', {
            'fields': ('address', 'phone', 'email', 'working_hours')
        }),
    )

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'added_date', 'is_published', 'order')
    list_filter = ('is_published', 'added_date')
    search_fields = ('question', 'answer')
    list_editable = ('is_published', 'order')
    readonly_fields = ('added_date',)

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')
    search_fields = ('name', 'website')

from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('client', 'item_count', 'total', 'updated_at')
    inlines = [CartItemInline]
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('client__company_name', 'client__user__username')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'furniture', 'quantity', 'subtotal')
    list_filter = ('cart__client',)
    search_fields = ('furniture__title', 'cart__client__company_name')