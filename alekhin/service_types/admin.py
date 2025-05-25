from django.contrib import admin
from .models import ServiceType


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    readonly_fields = ['id']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'id')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # При редактировании
            return self.readonly_fields
        return ['id']