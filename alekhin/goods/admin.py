from django.contrib import admin
from .models import Good


@admin.register(Good)
class GoodAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'article', 'service_direction', 'price', 'sizes', 
        'enabled', 'has_image', 'created_at'
    )
    list_filter = (
        'enabled', 'service_direction', 'created_at'
    )
    search_fields = (
        'name', 'article', 'description', 'sizes', 'product_care', 
        'important', 'contraindications'
    )
    list_editable = ('enabled', 'price')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'image', 'service_direction', 'article', 'price', 'enabled')
        }),
        ('Описание и характеристики', {
            'fields': ('description', 'sizes', 'product_care'),
            'classes': ('collapse',)
        }),
        ('Важная информация', {
            'fields': ('important', 'contraindications'),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
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