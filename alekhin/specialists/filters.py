from django.db.models import Q
from django_filters import rest_framework as filters
from .models import Specialist

class SpecialistFilter(filters.FilterSet):
    directions = filters.NumberFilter(field_name='directions', lookup_expr='in')

    class Meta:
        model = Specialist
        fields = ['directions']