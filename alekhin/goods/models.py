# alekhin/goods/models.py
# Исправленная модель Good с необязательным полем article

from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from images.models import Image
import uuid


class Good(models.Model):
    # Основная информация
    name = models.CharField(max_length=255, verbose_name="Название товара")
    image = models.CharField(max_length=255, blank=True, null=True, verbose_name="Изображение товара")
    service_direction = models.PositiveIntegerField(verbose_name="ID направления услуги")
    article = models.CharField(max_length=100, blank=True, null=True, verbose_name="Артикул")  # ✅ ИСПРАВЛЕНО!
    price = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Цена"
    )
    
    # Описание и характеристики
    description = models.TextField(blank=True, verbose_name="Описание")
    sizes = models.CharField(blank=True, verbose_name="Размеры")
    product_care = models.TextField(blank=True, verbose_name="Уход за товаром")
    important = models.TextField(blank=True, verbose_name="Важная информация")
    contraindications = models.TextField(blank=True, verbose_name="Противопоказания")
    
    # Служебные поля
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug")
    enabled = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['service_direction']),
            models.Index(fields=['enabled']),
            models.Index(fields=['slug']),
            models.Index(fields=['article']),
        ]
    
    def __str__(self):
        if self.article:
            return f"{self.name} (арт. {self.article})"
        else:
            return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            from unidecode import unidecode
            
            # Создаем slug на основе названия
            base_slug = slugify(unidecode(self.name))
            slug = base_slug
            counter = 1
            
            # Проверяем уникальность slug
            while Good.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        super().save(*args, **kwargs)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if not self.name or not self.name.strip():
            raise ValidationError("Название товара не может быть пустым")
        
        if self.price < 0:
            raise ValidationError("Цена не может быть отрицательной")
        
        # Проверяем уникальность артикула только если он указан
        if self.article and self.article.strip():
            existing_good = Good.objects.filter(article=self.article.strip()).exclude(pk=self.pk)
            if existing_good.exists():
                raise ValidationError("Товар с таким артикулом уже существует")