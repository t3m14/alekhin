from django.db import models

class Specialist(models.Model):
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=255)
    directions = models.JSONField(default=list)
    titles = models.JSONField(default=list)
    experience = models.IntegerField()
    is_reliable = models.BooleanField(default=False)
    degree = models.CharField(max_length=255, null=True, blank=True)
    # education = models.CharField(max_length=255, null=True, blank=True)
    biography = models.TextField(null=True, blank=True)
    serts = models.JSONField(default=list)
