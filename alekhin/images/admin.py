from django.contrib import admin
from .models import ImageModel


@admin.register(ImageModel)
class ImageModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'original_filename', 'width', 'height', 'file_size', 'created_at']
    list_filter = ['created_at']
    search_fields = ['original_filename', 'id']
    readonly_fields = ['id', 'file_size', 'width', 'height', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'original_filename')
        }),
        ('Изображения', {
            'fields': ('image', 'cropped_image')
        }),
        ('Метаданные', {
            'fields': ('file_size', 'width', 'height', 'created_at', 'updated_at')
        }),
    )