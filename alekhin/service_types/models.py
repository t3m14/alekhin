from django.db import models


class ServiceType(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название типа услуги')

    class Meta:
        db_table = 'service_types'
        verbose_name = 'Тип услуги'
        verbose_name_plural = 'Типы услуг'
        ordering = ['name']

    def __str__(self):
        return self.name
