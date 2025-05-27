from django_filters import rest_framework as filters
from .models import Request
from specialists.models import Specialist


class RequestFilter(filters.FilterSet):
    # Фильтрация по типу заявки
    is_service = filters.BooleanFilter()
    is_goods = filters.BooleanFilter()
    is_analysis = filters.BooleanFilter()
    
    # Фильтрация по направлению (только для услуг)
    service_direction = filters.CharFilter(lookup_expr='icontains')
    service_type = filters.CharFilter(lookup_expr='icontains')
    
    # Фильтрация по специалисту (только для услуг)
    specialist = filters.ModelChoiceFilter(
        queryset=Specialist.objects.all()
    )
    
    # Фильтрация по статусу
    is_new = filters.BooleanFilter()
    
    # Фильтрация по дате
    created_at = filters.DateFromToRangeFilter()
    created_at_gte = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Request
        fields = [
            'is_service', 'is_goods', 'is_analysis', 
            'service_direction', 'service_type', 'specialist', 'is_new'
        ]
