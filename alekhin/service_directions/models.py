from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()

class ServiceDirection(models.Model):
    name = models.CharField(max_length=255, verbose_name="Service Direction Name")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    types = models.JSONField(default=list, verbose_name="Service Type IDs")
    questions_answers = models.JSONField(default=list, verbose_name="Questions and Answers")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service Direction"
        verbose_name_plural = "Service Directions"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            from unidecode import unidecode
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)