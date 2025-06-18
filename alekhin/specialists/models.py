# alekhin/specialists/models.py
# Исправленная модель Specialist

from django.db import models

class Specialist(models.Model):
    # ОБЯЗАТЕЛЬНЫЕ ПОЛЯ
    name = models.CharField(max_length=255, verbose_name="Имя специалиста")
    image = models.CharField(max_length=255, verbose_name="Изображение")
    
    # ОПЦИОНАЛЬНЫЕ ПОЛЯ
    directions = models.JSONField(default=list, verbose_name="Направления деятельности")
    titles = models.JSONField(default=list, verbose_name="Должности")
    experience = models.IntegerField(null=True, blank=True, verbose_name="Опыт работы (лет)")  # ✅ ИСПРАВЛЕНО!
    is_reliable = models.BooleanField(default=False, verbose_name="Проверенный специалист")
    degree = models.CharField(max_length=255, null=True, blank=True, verbose_name="Степень/звание")
    biography = models.TextField(null=True, blank=True, verbose_name="Биография")
    serts = models.JSONField(default=list, verbose_name="Сертификаты")
    
    class Meta:
        verbose_name = "Специалист"
        verbose_name_plural = "Специалисты"
        ordering = ['name']
    
    def __str__(self):
        return self.name