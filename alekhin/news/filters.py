# alekhin/news/filters.py
from django_filters import rest_framework as filters
from .models import News


class NewsFilter(filters.FilterSet):
    # Фильтрация по заголовку
    title = filters.CharFilter(lookup_expr='icontains')
    
    # Фильтрация по направлению услуги
    service_direction = filters.NumberFilter()
    
    # Фильтрация по времени чтения
    time_to_read = filters.NumberFilter()
    time_to_read_gte = filters.NumberFilter(field_name='time_to_read', lookup_expr='gte')
    time_to_read_lte = filters.NumberFilter(field_name='time_to_read', lookup_expr='lte')
    time_to_read_range = filters.RangeFilter(field_name='time_to_read')
    
    # Фильтрация по статусу
    enabled = filters.BooleanFilter()
    
    # Фильтрация по дате создания
    created_at = filters.DateFromToRangeFilter()
    created_at_gte = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = News
        fields = [
            'title', 'service_direction', 'time_to_read', 'enabled'
        ]