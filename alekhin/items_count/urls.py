from django.urls import path
from . import views

urlpatterns = [
    # Основные эндпойнты
    path('', views.items_count, name='items_count'),
    path('stats/', views.detailed_stats, name='detailed_stats'),
    path('endpoints/', views.available_endpoints, name='available_endpoints'),
    
    # Удобные эндпойнты для конкретных моделей
    path('specialists/', views.specialists_count, name='specialists_count'),
    path('images/', views.images_count, name='images_count'),
    path('services/', views.services_count, name='services_count'),
    path('job_titles/', views.job_titles_count, name='job_titles_count'),
    path('tests/', views.tests_count, name='tests_count'),
    path('goods/', views.goods_count, name='goods_count'),
    path('requests/', views.requests_count, name='requests_count'),
    path('service_types/', views.service_types_count, name='service_types_count'),
]
