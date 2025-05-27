from django_filters import rest_framework as filters
from .models import Good


class GoodFilter(filters.FilterSet):
    # Фильтрация по названию
    name = filters.CharFilter(lookup_expr='icontains')
    
    # Фильтрация по направлению услуги
    service_direction = filters.NumberFilter()
    
    # Фильтрация по артикулу
    article = filters.CharFilter(lookup_expr='icontains')
    
    # Фильтрация по цене
    price = filters.NumberFilter()
    price_gte = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_lte = filters.NumberFilter(field_name='price', lookup_expr='lte')
    price_range = filters.RangeFilter(field_name='price')
    
    # Фильтрация по размерам
    sizes = filters.CharFilter(lookup_expr='icontains')
    
    # Фильтрация по статусу
    enabled = filters.BooleanFilter()
    
    # Фильтрация по наличию изображения
    has_image = filters.BooleanFilter(field_name='image', lookup_expr='isnull', exclude=True)
    
    # Фильтрация по дате создания
    created_at = filters.DateFromToRangeFilter()
    created_at_gte = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Good
        fields = [
            'name', 'service_direction', 'article', 'price', 'sizes', 'enabled'
        ]
