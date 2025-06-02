import django_filters
from django.db.models import Q
from .models import Service

class ServiceFilter(django_filters.FilterSet):
        model = Service
        fields = []
 