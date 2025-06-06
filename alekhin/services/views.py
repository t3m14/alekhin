import watson
from django.shortcuts import render
from .models import *

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as django_filters
from .serializers import *
from .filters import ServiceFilter
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from .models import Service


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
    template_name = 'rest_framework/filters/django_filters.html'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return []

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Остальные фильтры
        job_titles = self.request.query_params.get('job_titles', None)
        if job_titles:
            queryset = queryset.filter(job_titles__icontains=job_titles.rstrip('/'))
            
        service_type = self.request.query_params.get('service_type', None)
        if service_type:
            queryset = queryset.filter(service_type__iexact=service_type)

        service_direction = self.request.query_params.get('service_direction', None)
        if service_direction:
            queryset = queryset.filter(service_direction__iexact=service_direction)

            # Поиск без учета регистра
            search_query = self.request.query_params.get('search', None)
            if search_query:
                queryset = queryset.filter(
                    Q(name__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(slug__icontains=search_query)
                )        
        return queryset