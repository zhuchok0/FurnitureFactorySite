from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count, F, DecimalField, Q
from django.db.models.functions import Coalesce
from .models import Furniture, Client, Order, Type, News, Term, Employee, Vacancy, PromoCode, Design, Review
from statistics import median, mode
from decimal import Decimal
from datetime import date, datetime, timedelta
from django.contrib.auth.decorators import user_passes_test, login_required
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import calendar
from sklearn.linear_model import LinearRegression
import numpy as np
from .forms import OrderForm, ReviewForm, ClientRegistrationForm
from django.utils import timezone
import requests
import re
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
import pytz
import logging

logger = logging.getLogger(__name__)


def main(request):
    latest_news = News.objects.first() 

    clients_alphabetical = Client.objects.order_by('company_name')
    furniture_alphabetical = Furniture.objects.order_by('title')
    
    orders = Order.objects.select_related('furniture')
    total_sales = sum(order.total_price for order in orders)
    
    order_totals = [float(order.total_price) for order in orders]
    
    if order_totals:
        avg_sales = sum(order_totals) / len(order_totals)
        median_sales = median(order_totals)
        try:
            mode_sales = mode(order_totals)
        except:
            mode_sales = None
    else:
        avg_sales = 0
        median_sales = 0
        mode_sales = None
    
    client_ages = [client.age for client in Client.objects.filter(age__isnull=False)]
    
    if client_ages:
        avg_age = sum(client_ages) / len(client_ages)
        median_age = median(client_ages)
    else:
        avg_age = 0
        median_age = 0
    
    popular_types = Type.objects.annotate(
        order_count=Count('furniture__order')
    ).order_by('-order_count')
    
    most_popular_type = popular_types.first()
    
    profitable_types = Type.objects.annotate(
        total_revenue=Coalesce(
            Sum(
                F('furniture__order__quantity') * F('furniture__price'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ),
            Decimal(0)
        )
    ).order_by('-total_revenue')
    
    most_profitable_type = profitable_types.first()
    
    all_types_stats = []
    for type_obj in Type.objects.all():
        order_count = type_obj.furniture_set.aggregate(
            total=Count('order')
        )['total'] or 0
        
        revenue = type_obj.furniture_set.aggregate(
            total=Coalesce(
                Sum(
                    F('order__quantity') * F('price'),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                ),
                Decimal(0)
            )
        )['total'] or Decimal(0)
        
        all_types_stats.append({
            'name': type_obj.name,
            'order_count': order_count,
            'revenue': revenue,
        })

    client_timezone_info = None
    current_date_in_tz = None
    timezone_updated_at = None
    calendar_html = None
    weather_info = None
    video_data = None

    if request.user.is_authenticated and request.user.groups.filter(name='Client').exists():
        logger.info(f'Client {request.user.username} accessed main page')
        try:
            client_profile = request.user.client_profile
            tz_name = client_profile.timezone if client_profile.timezone else 'UTC'

            if request.method == 'POST' and 'timezone' in request.POST:
                new_tz = request.POST.get('timezone')
                if new_tz in pytz.common_timezones:  
                    client_profile.timezone = new_tz
                    client_profile.save()
                    return redirect('main') 

            timezone.activate(tz_name)
            current_date_in_tz = timezone.now().date() 
            timezone_updated_at = client_profile.timezone_updated_at
            
            today = current_date_in_tz
            cal = calendar.monthcalendar(today.year, today.month)
            calendar_html = '<table border="1" style="border-collapse: collapse;">'
            calendar_html += f'<caption>{today.strftime("%B %Y")}</caption>'
            calendar_html += '<thead><tr><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Sat</th><th>Sun</th></tr></thead><tbody>'
            for week in cal:
                calendar_html += '<tr>'
                for day in week:
                    if day == 0:
                        calendar_html += '<td></td>'
                    else:
                        if day == today.day:
                            calendar_html += f'<td style="background-color: #ffeb3b;"><strong>{day}</strong></td>'
                        else:
                            calendar_html += f'<td>{day}</td>'
                calendar_html += '</tr>'
            calendar_html += '</tbody></table>'
            
            client_timezone_info = {
                'name': tz_name,
                'current_date': current_date_in_tz,
                'timezone_updated': timezone_updated_at,
                'calendar': calendar_html,
            }

            # for weather
            appid = settings.OPENWEATHER_API_KEY

            city = 'Minsk'
            match = re.search(r'\w+/(?P<city_name>\w+)', tz_name)
            if match:
                city = match.group('city_name')

            url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={appid}'
            weather_info = None
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                if data.get("cod") == 200:
                    weather_info = {
                        'city': data['name'],
                        'temp': data['main']['temp'],
                        'icon': data['weather'][0]['icon'],
                        'description': data['weather'][0]['description'],
                    }
            except requests.RequestException as e:
                logger.warning(f'Weather API failed: {e}')

            api_key = settings.YOUTUBE_API_KEY
            search_video_id = 'qlpE7SFtMPQ'
            url = f'https://www.googleapis.com/youtube/v3/videos?id={search_video_id}&key={api_key}&part=snippet,contentDetails,status'
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                if data.get('items'):
                    item = data['items'][0]
                    video_data = {
                        'id': item['id'],
                        'title': item['snippet']['title'],
                    }
            except requests.RequestException:
                video_data = None

        except requests.RequestException as e:
            logger.warning(f'YouTube API failed: {e}')
    
    context = {
        'latest_news': latest_news,
        'clients': clients_alphabetical,
        'furniture_list': furniture_alphabetical,
        'total_sales': total_sales,
        'avg_sales': round(avg_sales, 2) if avg_sales else 0,
        'median_sales': round(median_sales, 2) if median_sales else 0,
        'mode_sales': mode_sales,
        'order_totals': order_totals,
        'avg_age': round(avg_age, 1) if avg_age else 0,
        'median_age': median_age,
        'client_ages': client_ages,
        'most_popular_type': most_popular_type,
        'most_profitable_type': most_profitable_type,
        'all_types_stats': all_types_stats,
        'client_info': client_timezone_info,
        'timezones': pytz.common_timezones,
        'weather_info': weather_info,
        'video_data': video_data
    }
    
    return render(request, 'main.html', context)

def news_list(request):
    news_items = News.objects.all().order_by('-created_date')
    return render(request, 'news_list.html', {'news_items': news_items})

def about(request):
    return render(request, 'about.html')

def terms_list(request):
    terms = Term.objects.all()
    
    search_query = request.GET.get('search', '')
    if search_query:
        terms = terms.filter(
            Q(question__icontains=search_query) |
            Q(answer__icontains=search_query)
        )
    
    sort_by = request.GET.get('sort', 'question')
    if sort_by == 'question':
        terms = terms.order_by('question')
    elif sort_by == '-question':
        terms = terms.order_by('-question')
    else:
        terms = terms.order_by('question')
    
    context = {
        'terms': terms,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'terms_list.html', context)

def contacts(request):
    employees = Employee.objects.select_related('position').all()
    return render(request, 'contacts.html', {'employees': employees})

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def vacancies_list(request):
    vacancies = Vacancy.objects.filter(is_active=True).order_by('-created_date')
    return render(request, 'vacancies_list.html', {'vacancies': vacancies})

def promocodes_list(request):
    today = date.today()
    
    active_promocodes = PromoCode.objects.filter(
        is_active=True,
        valid_from__lte=today,
        valid_to__gte=today
    ).order_by('valid_to')
    
    all_promocodes = PromoCode.objects.all()
    
    archive_promocodes = []
    for promo in all_promocodes:
        if not (promo.is_active and promo.valid_from <= today and promo.valid_to >= today):
            archive_promocodes.append(promo)
    
    context = {
        'active_promocodes': active_promocodes,
        'archive_promocodes': archive_promocodes,
    }
    return render(request, 'promocodes_list.html', context)


def get_chart():
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return f'data:image/png;base64,{image_base64}'


def is_admin(user):
    return user.is_superuser or user.is_staff


@user_passes_test(is_admin, login_url='main')
def analytics_dashboard(request):
    logger.info(f'Admin {request.user.username} accessed analytics dashboard')

    # Furniture Price List
    price_list = Furniture.objects.all().order_by('title').values('title', 'price')
    
    # Clients grouped by city 
    clients_by_city = {}
    for city in Client.objects.values_list('city', flat=True).distinct():
        clients = Client.objects.filter(city=city).values_list('company_name', flat=True)
        clients_by_city[city] = list(clients)
    
    # Revenue comparison by city
    orders = Order.objects.select_related('client', 'furniture', 'furniture__design')
    
    data = []
    for order in orders:
        data.append({
            'client_city': order.client.city,
            'total': float(order.total_price),
        })
    
    df = pd.DataFrame(data)
    
    if not df.empty:
        city_revenue = df.groupby('client_city')['total'].sum().sort_values(ascending=False)
        
        plt.figure(figsize=(12, 6))
        plt.bar(range(len(city_revenue)), city_revenue.values, color='skyblue')
        plt.xticks(range(len(city_revenue)), city_revenue.index, rotation=45, ha='right')
        plt.title('Revenue by City', fontsize=16)
        plt.xlabel('City', fontsize=12)
        plt.ylabel('Revenue ($)', fontsize=12)
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        city_chart = get_chart()
    else:
        city_chart = None
    
    # Design analysis 
    design_data = []
    for order in orders:
        if order.furniture.design:
            design_name = order.furniture.design.name
            design_data.append({
                'design': design_name,
                'total': float(order.total_price),
            })
    
    df_design = pd.DataFrame(design_data)
    
    if not df_design.empty:
        design_orders = {}
        for order in orders:
            if order.furniture.design:
                design = order.furniture.design.name
                design_orders[design] = design_orders.get(design, 0) + 1
        
        sorted_designs = sorted(design_orders.items(), key=lambda x: x[1], reverse=True)
        top_3_designs = [{'name': d[0], 'orders': d[1]} for d in sorted_designs[:3]]
        bottom_3_designs = [{'name': d[0], 'orders': d[1]} for d in sorted_designs[-3:]]
        
        design_revenue = df_design.groupby('design')['total'].sum()
        
        plt.figure(figsize=(8, 8))
        plt.pie(design_revenue.values, labels=design_revenue.index, autopct='%1.1f%%')
        plt.title('Revenue by Design', fontsize=16)
        design_pie_chart = get_chart()
    else:
        top_3_designs = []
        bottom_3_designs = []
        design_pie_chart = None
    
    # Monthly revenue by furniture type line chart
    type_monthly_data = []
    for order in orders:
        if order.delivery_date:
            for furniture_type in order.furniture.type.all():
                type_monthly_data.append({
                    'type': furniture_type.name,
                    'month': order.delivery_date.strftime('%Y-%m'),
                    'total': float(order.total_price),
                })
    
    if type_monthly_data:
        df_type = pd.DataFrame(type_monthly_data)
        
        df_type_grouped = df_type.groupby(['type', 'month'])['total'].sum().reset_index()
        
        df_type_grouped = df_type_grouped.sort_values('month')
        
        unique_types = df_type_grouped['type'].unique()
        
        plt.figure(figsize=(14, 7))
        
        for furniture_type in unique_types:
            type_data = df_type_grouped[df_type_grouped['type'] == furniture_type]
            plt.plot(type_data['month'], type_data['total'], 'o-', label=furniture_type, linewidth=2, markersize=6)
        
        plt.title('Monthly Revenue by Furniture Type', fontsize=16)
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Revenue ($)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        type_trend_chart = get_chart()
    else:
        type_trend_chart = None

    # Yearly statistics (table)
    yearly_data = []
    for order in orders:
        if order.order_date:
            yearly_data.append({
                'year': order.order_date.year,
                'total': float(order.total_price),
            })

    if yearly_data:
        df_yearly = pd.DataFrame(yearly_data)
        
        yearly_stats = df_yearly.groupby('year').agg({
            'total': ['sum', 'count']
        }).reset_index()
        
        yearly_stats.columns = ['year', 'revenue', 'orders_count']
        yearly_stats = yearly_stats.sort_values('year')
        
        yearly_stats['revenue'] = yearly_stats['revenue'].round(2)
        
        yearly_stats_list = yearly_stats.to_dict('records')
    else:
        yearly_stats_list = None

    # Monthly sales line chart for current year 
    current_year = date.today().year
    monthly_data = []

    for order in orders:
        if order.delivery_date and order.delivery_date.year == current_year:
            monthly_data.append({
                'month': order.delivery_date.month,
                'total': float(order.total_price),
            })

    if monthly_data:
        df_monthly = pd.DataFrame(monthly_data)
        
        monthly_stats = df_monthly.groupby('month')['total'].sum().reset_index()
        
        all_months = pd.DataFrame({'month': range(1, 13)})
        monthly_stats = all_months.merge(monthly_stats, on='month', how='left').fillna(0)
        
        month_names = [calendar.month_name[i] for i in range(1, 13)]
        
        plt.figure(figsize=(12, 6))
        plt.plot(month_names, monthly_stats['total'], 'o-', color='blue', linewidth=2, markersize=8)
        plt.title(f'Monthly Sales for {current_year}', fontsize=16)
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Revenue ($)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        monthly_sales_chart = get_chart()
    else:
        monthly_sales_chart = None

    # Sales forecast for next 3 months
    monthly_sales_data = []
    for order in orders:
        if order.order_date:
            month_key = order.order_date.strftime('%Y-%m')
            monthly_sales_data.append({
                'month': month_key,
                'month_num': (order.order_date.year - 2020) * 12 + order.order_date.month,
                'total': float(order.total_price),
            })
    
    if monthly_sales_data:
        df_sales = pd.DataFrame(monthly_sales_data)
        df_monthly = df_sales.groupby(['month_num', 'month'])['total'].sum().reset_index()
        df_monthly = df_monthly.sort_values('month_num')
        
        if len(df_monthly) >= 3:
            # Linear regression
            X = df_monthly['month_num'].values.reshape(-1, 1)
            y = df_monthly['total'].values
            model = LinearRegression()
            model.fit(X, y)
            
            last_month = df_monthly['month_num'].max()
            future_months = np.arange(last_month + 1, last_month + 4).reshape(-1, 1)
            predictions = model.predict(future_months)
            
            last_date = Order.objects.filter(order_date__isnull=False).last().order_date
            future_dates = []
            for i in range(1, 4):
                next_date = last_date.replace(day=1) + timedelta(days=32*i)
                future_dates.append(next_date.strftime('%B %Y'))
            
            sales_forecast = list(zip(future_dates, predictions.round(2)))
            
            slope = model.coef_[0]
            trend_direction = "increase" if slope > 0 else "decrease"
        else:
            sales_forecast = None
            trend_direction = None
            slope = None
    else:
        sales_forecast = None
        trend_direction = None
        slope = None

    # Linear sales trend 
    trend_data = []
    for order in orders:
        if order.order_date:
            month_num = (order.order_date.year - 2020) * 12 + order.order_date.month
            trend_data.append({
                'month_num': month_num,
                'total': float(order.total_price),
            })
    
    if len(trend_data) >= 2:
        df_trend = pd.DataFrame(trend_data)
        df_trend_monthly = df_trend.groupby('month_num')['total'].sum().reset_index()
        df_trend_monthly = df_trend_monthly.sort_values('month_num')
        
        if len(df_trend_monthly) >= 2:
            X = df_trend_monthly['month_num'].values.reshape(-1, 1)
            y = df_trend_monthly['total'].values
            model_trend = LinearRegression()
            model_trend.fit(X, y)
            
            trend_line = model_trend.predict(X)
            
            trend_months = []
            for _, row in df_trend_monthly.iterrows():
                year = int(2020 + (row['month_num'] - 1) // 12)
                month = int((row['month_num'] - 1) % 12 + 1)
                d = date(year, month, 1)
                trend_months.append(d.strftime('%Y-%m'))
            
            plt.figure(figsize=(14, 7))
            
            actual_sales = df_trend_monthly['total'].values
            plt.plot(trend_months, actual_sales, 'o-', color='blue', label='Actual Sales', linewidth=2, markersize=8)
            plt.plot(trend_months, trend_line, '--', color='red', label=f'Linear Trend (R² = {model_trend.score(X, y):.3f})', linewidth=2)
            
            plt.title('Sales Trend with Linear Regression', fontsize=16)
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Revenue ($)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            trend_chart = get_chart()
            
            trend_slope = model_trend.coef_[0]
            r_squared = model_trend.score(X, y)
            trend_message = f"Monthly trend: {'+' if trend_slope > 0 else ''}{trend_slope:.2f} $ per month"
        else:
            trend_chart = None
            trend_message = "Not enough data for trend (minimum 2 months required)"
            r_squared = None
    else:
        trend_chart = None
        trend_message = "No data available"
        r_squared = None


    context = {
        'price_list': price_list,
        'clients_by_city': clients_by_city,
        'city_chart': city_chart,
        'top_3_designs': top_3_designs,
        'bottom_3_designs': bottom_3_designs,
        'design_pie_chart': design_pie_chart,
        'type_trend_chart': type_trend_chart,
        'yearly_stats': yearly_stats_list,
        'monthly_sales_chart': monthly_sales_chart, 
        'current_year': current_year, 
        'sales_forecast': sales_forecast,
        'trend_direction': trend_direction,
        'slope': slope,
        'trend_chart': trend_chart,
        'trend_message': trend_message,
        'r_squared': r_squared,
    }
        
    return render(request, 'analytics_dashboard.html', context)

def catalog(request):
    types = Type.objects.all().annotate(
        furniture_count=Count('furniture')
    ).order_by('name')
    
    designs = Design.objects.all().annotate(
        furniture_count=Count('furniture')
    ).order_by('name')
    
    sort_by = request.GET.get('sort', 'price_asc')
    
    if sort_by == 'price_asc':
        furniture_list = Furniture.objects.all().order_by('price')
    elif sort_by == 'price_desc':
        furniture_list = Furniture.objects.all().order_by('-price')
    else:
        furniture_list = Furniture.objects.all().order_by('price')
    
    for furniture in furniture_list:
        furniture.type_names = ', '.join([t.name for t in furniture.type.all()])
        furniture.design_name = furniture.design.name if furniture.design else 'No design'
    
    context = {
        'types': types,
        'designs': designs,
        'furniture_list': furniture_list,
        'sort_by': sort_by,
    }
    return render(request, 'catalog.html', context)

def is_client(user):
    return user.is_authenticated and user.groups.filter(name='Client').exists()

@login_required
@user_passes_test(is_client)
def client_orders(request):
    try:
        client_profile = request.user.client_profile
        orders = Order.objects.filter(client=client_profile).order_by('-order_date')
    except Client.DoesNotExist:
        orders = []
    return render(request, 'client_orders.html', {'orders': orders})

@login_required
@user_passes_test(is_client)
def create_order(request):
    client_profile, created = Client.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = client_profile
            order.order_date = date.today()
            order.save()
            logger.info(f'Order #{order.id} created by {client_profile.company_name} (user {request.user.username})')
            return redirect('client_orders')
    else:
        form = OrderForm()

    return render(request, 'order_form.html', {'form': form})

def reviews_list(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'reviews.html', {'reviews': reviews})

@login_required
def add_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reviews_list')
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form})

@user_passes_test(is_admin, login_url='main')
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated successfully.')
            logger.info(f'Review {review.pk} edited by admin {request.user.username}')
            return redirect('reviews_list')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'edit_review.html', {'form': form, 'review': review})

@user_passes_test(is_admin, login_url='main')
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted successfully.')
        logger.info(f'Review {review.pk} deleted by admin {request.user.username}')
        return redirect('reviews_list')
    return render(request, 'confirm_delete_review.html', {'review': review})

def register_client(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info(f'New client registered: {user.username}')
            login(request, user) 
            return redirect('main')
    else:
        form = ClientRegistrationForm()
    return render(request, 'registration/register_client.html', {'form': form})

def is_employee(user):
    return user.is_authenticated and user.groups.filter(name='Employee').exists()

@user_passes_test(is_employee, login_url='main')
def employee_dashboard(request):
    clients = Client.objects.all().order_by('company_name')
    orders = Order.objects.select_related('client', 'furniture').all().order_by('-order_date')
    context = {
        'clients': clients,
        'orders': orders,
    }
    return render(request, 'employee_dashboard.html', context)
