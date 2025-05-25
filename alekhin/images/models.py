import uuid
import os
from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


class ImageModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_filename = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/')
    cropped_image = models.ImageField(upload_to='images/', null=True, blank=True)
    file_size = models.PositiveIntegerField()
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'images'
        verbose_name = 'Image'
        verbose_name_plural = 'Images'

    def __str__(self):
        return f"{self.original_filename} ({self.id})"

    def save(self, *args, **kwargs):
        if self.image:
            # Конвертируем в WebP и сжимаем
            self.image = self.convert_to_webp(self.image)
            
            # Получаем размеры изображения
            with Image.open(self.image) as img:
                self.width, self.height = img.size
                
        super().save(*args, **kwargs)

    def convert_to_webp(self, image_field, quality=85):
        """Конвертирует изображение в формат WebP"""
        with Image.open(image_field) as img:
            # Конвертируем в RGB если необходимо
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Создаем BytesIO объект для сохранения
            output = BytesIO()
            
            # Сохраняем в формате WebP с сжатием
            img.save(output, format='WebP', quality=quality, optimize=True)
            output.seek(0)
            
            # Создаем новое имя файла с расширением .webp
            name = os.path.splitext(image_field.name)[0] + '.webp'
            
            return ContentFile(output.read(), name=name)

    def create_cropped_version(self):
        """Создает обрезанную версию изображения для мобильных устройств"""
        if not self.image:
            return
            
        with Image.open(self.image.path) as img:
            # Если ширина больше 600px, обрезаем
            if img.width > 600:
                # Вычисляем новую высоту с сохранением пропорций
                ratio = 600 / img.width
                new_height = int(img.height * ratio)
                
                # Изменяем размер
                resized_img = img.resize((600, new_height), Image.Resampling.LANCZOS)
                
                # Сохраняем в BytesIO
                output = BytesIO()
                resized_img.save(output, format='WebP', quality=85, optimize=True)
                output.seek(0)
                
                # Создаем имя файла с префиксом _cropped
                name = os.path.splitext(self.image.name)[0] + '_cropped.webp'
                
                self.cropped_image.save(
                    name,
                    ContentFile(output.read()),
                    save=False
                )