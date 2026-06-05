"""
URL configuration for FurnitureFactory project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from main import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.main, name='main'),
    path('news/', views.news_list, name='news_list'),
    path('about/', views.about, name='about'), 
    path('terms/', views.terms_list, name='terms_list'), 
    path('contacts/', views.contacts, name='contacts'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('vacancies/', views.vacancies_list, name='vacancies_list'),
    path('promocodes/', views.promocodes_list, name='promocodes_list'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('catalog/', views.catalog, name='catalog'),
    path('orders/', views.client_orders, name='client_orders'),
    path('order/new/', views.create_order, name='create_order'),
    path('reviews/', views.reviews_list, name='reviews_list'),
    path('reviews/add/', views.add_review, name='add_review'),
    re_path(r'^reviews/edit/(?P<pk>\d+)/$', views.edit_review, name='edit_review'),
    re_path(r'^reviews/delete/(?P<pk>\d+)/$', views.delete_review, name='delete_review'),
    path('register/', views.register_client, name='register'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
]


from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
