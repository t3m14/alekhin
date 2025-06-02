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
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return []

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Убираем фильтрацию по is_reliable (пункт 19)
        # if not self.request.user.is_authenticated:
        #     queryset = queryset.filter(is_reliable=True)
        
        # Фильтрация по enabled для неавторизованных пользователей
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(enabled=True)
        
        # Исправляем фильтрацию по направлениям
        direction_id = self.request.query_params.get('direction', None)
        directions_id = self.request.query_params.get('directions', None)
        
        if direction_id:
            try:
                direction_id = int(direction_id)
                queryset = queryset.filter(directions__contains=[direction_id])
            except (ValueError, TypeError):
                pass
                
        if directions_id:
            try:
                directions_id = int(directions_id)
                queryset = queryset.filter(directions__contains=[direction_id])
                # Если есть фильтрация по направлениям, то фильтруем по is_reliable
                if not self.request.user.is_authenticated:
                    queryset = queryset.filter(is_reliable=True)
            except (ValueError, TypeError):
                pass

        return queryset.distinct()