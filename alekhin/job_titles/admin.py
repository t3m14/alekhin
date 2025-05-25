from django.contrib import admin
from .models import JobTitle


@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    readonly_fields = ['id']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name',)
        }),
        ('Системная информация', {
            'fields': ('id',),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # При редактировании
            return self.readonly_fields
        return ['id']