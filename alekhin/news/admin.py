# alekhin/news/admin.py
from django.contrib import admin
from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'service_direction', 'time_to_read', 
        'enabled', 'has_image', 'created_at'
    )
    list_filter = (
        'enabled', 'service_direction', 'created_at', 'time_to_read'
    )
    search_fields = (
        'title', 'text', 'slug'
    )
    list_editable = ('enabled',)
    readonly_fields = ('slug', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'text', 'image', 'enabled')
        }),
        ('Дополнительная информация', {
            'fields': ('time_to_read', 'service_direction'),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': ('slug', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Есть изображение'
    
    def get_queryset(self, request):
        return super().get_queryset(request)


admin.site.site_header = 'Alekhin Admin'