from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ServiceDirection(models.Model):
    name = models.CharField(max_length=255, verbose_name="Service Direction Name")
    types = models.JSONField(default=list, verbose_name="Service Type IDs")
    questions_answers = models.JSONField(default=list, verbose_name="Questions and Answers")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service Direction"
        verbose_name_plural = "Service Directions"

    def __str__(self):
        return self.name