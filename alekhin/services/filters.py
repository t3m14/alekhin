import django_filters
from django.db.models import Q
from .models import Service

class ServiceFilter(django_filters.FilterSet):
    service_direction = django_filters.CharFilter(method='filter_service_direction')
    service_type = django_filters.CharFilter(method='filter_service_type')
    job_title = django_filters.CharFilter(method='filter_job_title')
    
    def filter_service_direction(self, queryset, name, value):
        """Фильтр по service_direction JSON полю"""
        return queryset.filter(service_direction__icontains=value)
    
    def filter_service_type(self, queryset, name, value):
        """Фильтр по service_type JSON полю"""
        return queryset.filter(service_type__icontains=value)
    
    def filter_job_title(self, queryset, name, value):
        """Фильтр по job_titles JSON полю"""
        return queryset.filter(job_titles__icontains=value)

    class Meta:
        model = Service
        fields = ['service_direction', 'service_type', 'job_title']
