from django.urls import path
from django_filters import rest_framework as filters
from .models import Service

class ServiceFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    service_direction = filters.CharFilter(lookup_expr='exact')
    service_type = filters.CharFilter(lookup_expr='exact')
    specialists = filters.ModelMultipleChoiceFilter(
        field_name='specialists',
        queryset=Service.objects.all(),
        to_field_name='id'
    )

    class Meta:
        model = Service
        fields = ['name', 'description', 'service_direction', 'service_type', 'specialists']