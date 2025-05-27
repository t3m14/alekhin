from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .utils import CachedItemCountService

# Импортируем модели
try:
    from specialists.models import Specialist
    from images.models import Image
    from services.models import Service
    from job_titles.models import JobTitle
    from goods.models import Good
    # Добавьте другие модели по мере необходимости
except ImportError:
    # Модели могут быть недоступны при первой миграции
    pass


def clear_related_cache(sender, **kwargs):
    """Очищает кеш для связанной модели"""
    model_name = sender._meta.model_name
    app_label = sender._meta.app_label
    
    # Очищаем кеш для этой модели
    CachedItemCountService.clear_cache()


# Регистрируем сигналы для всех моделей
models_to_watch = []

try:
    models_to_watch = [
        Specialist, Image, Service, JobTitle, Good
    ]
except NameError:
    pass

for model in models_to_watch:
    post_save.connect(clear_related_cache, sender=model)
    post_delete.connect(clear_related_cache, sender=model)
