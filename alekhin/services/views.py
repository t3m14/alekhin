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

        # Smart search
        search_query = self.request.query_params.get('search', None)        
        if search_query:
            search_query = search_query.strip()
            search_query =  search_query.lower()
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(service_direction__icontains=search_query) |
                Q(service_type__icontains=search_query)
            ).distinct()
            if not queryset.exists():
                search_query = search_query.capitalize()
                queryset = queryset.filter(
                    Q(name__icontains=search_query.capitalize()) |
                    Q(description__icontains=search_query.capitalize()) |
                    Q(service_direction__icontains=search_query.capitalize()) |
                    Q(service_type__icontains=search_query.capitalize())
                ).distinct()
                if not queryset.exists():
                    search_query = search_query.upper()
                    queryset = queryset.filter(
                        Q(name__icontains=search_query.upper()) |
                        Q(description__icontains=search_query.upper()) |
                        Q(service_direction__icontains=search_query.upper()) |
                        Q(service_type__icontains=search_query.upper())
                    ).distinct()
                if not queryset.exists():
                    search_query = search_query.title()
                    queryset = queryset.filter(
                        Q(name__icontains=search_query.title()) |
                        Q(description__icontains=search_query.title()) |
                        Q(service_direction__icontains=search_query.title()) |
                        Q(service_type__icontains=search_query.title())
                    ).distinct()
        return queryset