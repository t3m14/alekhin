from django_filters import rest_framework as filters
from .models import Test


class TestFilter(filters.FilterSet):
    # Фильтрация по названию
    name = filters.CharFilter(lookup_expr='icontains')
    
    # Фильтрация по направлению услуги
    service_direction = filters.NumberFilter()
    
    # Фильтрация по цене
    price = filters.NumberFilter()
    price_gte = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_lte = filters.NumberFilter(field_name='price', lookup_expr='lte')
    price_range = filters.RangeFilter(field_name='price')
    
    # Фильтрация по методу
    method = filters.CharFilter(lookup_expr='icontains')
    
    # Фильтрация по времени выполнения
    time = filters.CharFilter(lookup_expr='icontains')
    
    # Фильтрация по номенклатуре
    nomenclature = filters.CharFilter(lookup_expr='icontains')
    
    # Фильтрация по статусу
    enabled = filters.BooleanFilter()
    
    # Фильтрация по дате создания
    created_at = filters.DateFromToRangeFilter()
    created_at_gte = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Test
        fields = [
            'name', 'service_direction', 'price', 'method', 'time', 
            'nomenclature', 'enabled'
        ]
