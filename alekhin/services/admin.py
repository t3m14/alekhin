from django.contrib import admin
from .models import *

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'service_direction', 'service_type', 'specialists')
    list_filter = ('service_direction', 'service_type', 'specialists')
    search_fields = ('name', 'description', 'specialists__name')
    list_editable = ('price', 'service_direction', 'service_type', 'specialists')
    list_per_page = 25
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('specialists')



admin.site.site_header = 'Alekhin Admin'