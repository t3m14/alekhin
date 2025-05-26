from django.db.models import Q
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as django_filters
from .models import Specialist
from .serializers import SpecialistSerializer

class SpecialistFilter(django_filters.FilterSet):
    directions = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Specialist
        fields = ['directions']

class SpecialistViewSet(viewsets.ModelViewSet):
    serializer_class = SpecialistSerializer
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description', 'slug']
    filterset_class = SpecialistFilter
    # lookup_field = 'id'
    pagination_class = None
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return []

    def get_queryset(self):
        queryset = Specialist.objects.all().order_by('id')
    
        # Filter by is_reliable for non-authenticated users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_reliable=True)

        # Smart search
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(specialization__icontains=search_query) |
                Q(readings__icontains=search_query) |
                Q(contraindications__icontains=search_query) |
                Q(devices__icontains=search_query) |
                Q(need_to_have__icontains=search_query)
            ).distinct()

        return queryset