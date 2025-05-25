from django.contrib import admin
from .models import ServiceDirection

@admin.register(ServiceDirection)
class ServiceDirectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')