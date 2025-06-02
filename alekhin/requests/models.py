from django.db import models
from django.core.validators import EmailValidator
from specialists.models import Specialist


class Request(models.Model):
    # Основная информация
    name = models.CharField(max_length=255, verbose_name="Имя")
    email = models.EmailField(validators=[EmailValidator()], verbose_name="Email", blank=True)
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    
    # Типы заявок
    is_service = models.BooleanField(default=False, verbose_name="Медицинская услуга")
    is_goods = models.BooleanField(default=False, verbose_name="Товары")
    is_analysis = models.BooleanField(default=False, verbose_name="Анализы")
    
    # Информация об услуге (заполняется если is_service=True)
    service_name = models.CharField(max_length=255, blank=True, verbose_name="Название услуги")
    service_direction = models.CharField(max_length=255, blank=True, verbose_name="Направление услуги")
    service_type = models.CharField(max_length=255, blank=True, verbose_name="Тип услуги")
    specialist = models.ForeignKey(
        Specialist, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Специалист"
    )
    
    # Дополнительная информация
    additional_info = models.JSONField(default=dict, blank=True, verbose_name="Дополнительная информация")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    # Служебные поля
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_new = models.BooleanField(default=True, verbose_name="Новая заявка")  # По умолчанию всегда True
    
    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заявка от {self.name} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Проверяем, что выбран хотя бы один тип заявки
        if not any([self.is_service, self.is_goods, self.is_analysis]):
            raise ValidationError("Необходимо выбрать хотя бы один тип заявки")
        
        # Если выбрана услуга, проверяем обязательные поля
        if self.is_service and not self.service_name:
            raise ValidationError("Для медицинской услуги необходимо указать название")
    