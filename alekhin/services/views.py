from django.shortcuts import render
from .models import *

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as django_filters
from .serializers import *
from .filters import ServiceFilter
from django.db.models import Q, Case, When, IntegerField
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by('-created_at')
    serializer_class = ServiceSerializer
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ServiceFilter
    search_fields = ['name', 'description', 'slug']
    lookup_field = 'slug'
    read_only_fields = ['created_at', 'slug']
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return []

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # filter by job_titles
        job_titles = self.request.query_params.get('job_titles', None)
        if job_titles:
            queryset = queryset.filter(job_titles__icontains=job_titles.rstrip('/'))
            
        # filter by service_type
        service_type = self.request.query_params.get('service_type', None)
        if service_type:
            queryset = queryset.filter(service_type__iexact=service_type)

        # filter by service_direction
        service_direction = self.request.query_params.get('service_direction', None)
        if service_direction:
            queryset = queryset.filter(service_direction__iexact=service_direction)

        # Улучшенный поиск с приоритетом
        search_query = self.request.query_params.get('search', None)
        if search_query:
            search_query = search_query.strip()
            
            # Создаем Q объект для поиска
            search_filter = (
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(service_direction__icontains=search_query) |
                Q(service_type__icontains=search_query) |
                Q(slug__icontains=search_query)
            )
            
            # Применяем фильтр и сортируем по релевантности
            queryset = queryset.filter(search_filter).annotate(
                relevance=Case(
                    # Точное совпадение имени - высший приоритет
                    When(name__iexact=search_query, then=5),
                    # Начинается с поискового запроса
                    When(name__istartswith=search_query, then=4),
                    When(service_type__istartswith=search_query, then=3),
                    When(service_direction__istartswith=search_query, then=3),
                    # Содержит поисковый запрос
                    When(name__icontains=search_query, then=2),
                    When(description__icontains=search_query, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ).order_by('-relevance', '-created_at').distinct()
            
        return queryset
