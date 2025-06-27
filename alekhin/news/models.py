# alekhin/news/models.py
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.utils import timezone
import re
from unidecode import unidecode


class News(models.Model):
    # Основная информация
    title = models.CharField(max_length=255, verbose_name="Заголовок статьи")
    text = models.TextField(verbose_name="Текст статьи")
    image = models.CharField(max_length=255, blank=True, null=True, verbose_name="Изображение")
    time_to_read = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(1)],
        verbose_name="Время чтения (в минутах)",
        help_text="Время чтения статьи в минутах"
    )
    service_direction = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name="ID направления услуги",
        help_text="Связь с направлением услуги"
    )
    
    # Служебные поля
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug")
    enabled = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['service_direction']),
            models.Index(fields=['enabled']),
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(unidecode(self.title))
            slug = re.sub(r'-+', '-', slug)
            original_slug = slug
            counter = 1
            while News.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if not self.title or not self.title.strip():
            raise ValidationError("Заголовок статьи не может быть пустым")
        
        if not self.text or not self.text.strip():
            raise ValidationError("Текст статьи не может быть пустым")
        
        if self.time_to_read is not None and self.time_to_read < 1:
            raise ValidationError("Время чтения должно быть больше 0")