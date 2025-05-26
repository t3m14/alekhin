from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from specialists.models import Specialist
import re

class Service(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    main_image = models.CharField(max_length=255)
    procedure_number = models.IntegerField()
    procedure_duration = models.CharField(max_length=100, null=True, blank=True)
    rehab_duration = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    service_direction = models.IntegerField(null=True, blank=True)
    service_type = models.IntegerField(null=True, blank=True)
    specialists = models.JSONField(default=list)  # List of Specialist IDs
    readings = models.TextField(null=True, blank=True)
    contraindications = models.TextField(null=True, blank=True)
    devices = models.TextField(null=True, blank=True)
    need_to_have = models.TextField(null=True, blank=True)
    images = models.JSONField(default=list)
    serts = models.JSONField(default=list)
    enabled = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            from unidecode import unidecode
            slug = slugify(unidecode(self.name))
            slug = re.sub(r'-+', '-', slug)
            original_slug = slug
            counter = 1
            while Service.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


