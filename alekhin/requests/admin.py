from django.contrib import admin
from .models import Request


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'email', 'phone', 'get_request_types', 
        'service_name', 'specialist', 'is_new', 'created_at'
    )
    list_filter = (
        'is_service', 'is_goods', 'is_analysis', 'is_new', 
        'service_direction', 'specialist', 'created_at'
    )
    search_fields = ('name', 'email', 'phone', 'service_name', 'description')
    list_editable = ('is_new',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25
    
    fieldsets = (
        ('Контактная информация', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Тип заявки', {
            'fields': ('is_service', 'is_goods', 'is_analysis')
        }),
        ('Информация об услуге', {
            'fields': ('service_name', 'service_direction', 'service_type', 'specialist'),
            'classes': ('collapse',)
        }),
        ('Дополнительно', {
            'fields': ('description', 'additional_info')
        }),
        ('Служебная информация', {
            'fields': ('is_new', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_request_types(self, obj):
        types = []
        if obj.is_service:
            types.append('Услуги')
        if obj.is_goods:
            types.append('Товары')
        if obj.is_analysis:
            types.append('Анализы')
        return ', '.join(types) if types else 'Не указано'
    
    get_request_types.short_description = 'Тип заявки'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('specialist')
