from django.db import models


class JobTitle(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название должности')
    class Meta:
        db_table = 'job_titles'
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
        ordering = ['name']

    def __str__(self):
        return self.name