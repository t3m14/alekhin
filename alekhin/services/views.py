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

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by('-created_at')
    serializer_class = ServiceSerializer
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ServiceFilter
    search_fields = ['name', 'description', 'slug']
    lookup_field = 'slug'
    read_only_fields = ['created_at', 'slug']
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return []

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Smart search
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(service_direction__icontains=search_query) |
                Q(service_type__icontains=search_query) |
                Q(specialists__name__icontains=search_query)
            ).distinct()

        # Filtering
        service_direction_id = self.request.query_params.get('service_direction', None)
        if service_direction_id:
            queryset = queryset.filter(service_direction_id=service_direction_id)

        service_type_id = self.request.query_params.get('service_type', None)
        if service_type_id:
            queryset = queryset.filter(service_type_id=service_type_id)

        return queryset
    
