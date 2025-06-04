from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Specialist
from .serializers import SpecialistSerializer

class SpecialistViewSet(viewsets.ModelViewSet):
    queryset = Specialist.objects.all()
    serializer_class = SpecialistSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    template_name = 'rest_framework/filters/django_filters_form.html'
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return []

    def get_queryset(self):
        queryset = super().get_queryset()
        
        directions = self.request.query_params.get('directions', None)

        if directions:
            queryset = queryset.filter(directions=str(directions))
            
        return queryset.distinct()