from django.contrib import admin
from .models import Specialist


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')
    list_filter = ('name',)
    search_fields = ('name', 'image')
    list_editable = ('image',)
    list_per_page = 25
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('services')
    