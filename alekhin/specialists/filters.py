from django_filters import rest_framework as filters
from .models import Specialist

class SpecialistFilter(filters.FilterSet):
    # Убираем directions отсюда, будем фильтровать в get_queryset
    class Meta:
        model = Specialist
        fields = []  # Или другие поля, кроме directions
