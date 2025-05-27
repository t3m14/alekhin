from django.contrib import admin
from .models import Test


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'service_direction', 'price', 'method', 'time', 
        'enabled', 'created_at'
    )
    list_filter = (
        'enabled', 'service_direction', 'method', 'created_at'
    )
    search_fields = (
        'name', 'nomenclature', 'method', 'characteristic', 
        'rules', 'readings', 'contraindications'
    )
    list_editable = ('enabled', 'price')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'service_direction', 'price', 'enabled')
        }),
        ('Техническая информация', {
            'fields': ('nomenclature', 'method', 'time', 'characteristic'),
            'classes': ('collapse',)
        }),
        ('Медицинская информация', {
            'fields': ('rules', 'readings', 'contraindications', 'depends_to'),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': ('slug', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)


admin.site.site_header = 'Alekhin Admin'
