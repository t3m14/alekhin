from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
import uuid
from django.utils.text import slugify
import re
from unidecode import unidecode

class Test(models.Model):
    # Основная информация
    name = models.CharField(max_length=255, verbose_name="Название анализа")
    service_direction = models.PositiveIntegerField(verbose_name="ID направления услуги")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name="Стоимость анализа"
    )
    
    # Техническая информация
    nomenclature = models.CharField(max_length=255, blank=True, verbose_name="Номенклатура")
    method = models.CharField(max_length=255, blank=True, verbose_name="Метод определения")
    time = models.CharField(max_length=100, blank=True, verbose_name="Срок исполнения")
    characteristic = models.TextField(blank=True, verbose_name="Характеристика")
    
    # Медицинская информация
    rules = models.TextField(blank=True, verbose_name="Правила подготовки")
    readings = models.TextField(blank=True, verbose_name="Показания")
    contraindications = models.TextField(blank=True, verbose_name="Противопоказания")
    depends_to = models.CharField(max_length=255, blank=True, verbose_name="Зависит от")
    
    # Служебные поля
    enabled = models.BooleanField(default=True, verbose_name="Активен")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Анализ"
        verbose_name_plural = "Анализы"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['service_direction']),
            models.Index(fields=['enabled']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            from unidecode import unidecode
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if not self.name or not self.name.strip():
            raise ValidationError("Название анализа не может быть пустым")
        
        if self.price < 0:
            raise ValidationError("Стоимость не может быть отрицательной")

