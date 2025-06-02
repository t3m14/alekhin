from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as django_filters
from django.db.models import Q
from .models import Specialist
from .serializers import SpecialistSerializer
from .filters import SpecialistFilter

class SpecialistViewSet(viewsets.ModelViewSet):
    queryset = Specialist.objects.all()
    serializer_class = SpecialistSerializer
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter]
    filterset_class = SpecialistFilter
    search_fields = ['name', 'description']
    # Убираем lookup_field если не нужен
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return []

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по enabled для неавторизованных пользователей
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(enabled=True)
        
        # Фильтрация по направлениям
        direction_id = self.request.query_params.get('direction')
        directions_id = self.request.query_params.get('directions')
        
        target_direction = direction_id or directions_id
        
        if target_direction:
            try:
                target_direction = str(target_direction).rstrip('/')
                direction_int = int(target_direction)
                
                print(f"Filtering by direction: {direction_int}")
                
                # Попробуйте разные варианты в зависимости от структуры данных
                # Вариант 1: Если directions хранится как строка JSON
                # queryset = queryset.filter(directions__icontains=f'"{direction_int}"')
                
                # Вариант 2: Если это PostgreSQL с JSONField
                # queryset = queryset.filter(directions__overlap=[str(direction_int)])
                
                # Вариант 3: Если это массив строк в JSON
                queryset = queryset.filter(directions__icontains=str(direction_int))
                
                if not self.request.user.is_authenticated:
                    queryset = queryset.filter(is_reliable=True)
                    
            except (ValueError, TypeError) as e:
                print(f"Error parsing direction: {e}")
                return queryset.none()

        print(f"Final queryset count: {queryset.count()}")
        return queryset.distinct()
