from django.core.cache import cache
from django.conf import settings
from .services import ItemCountService
import json


class CachedItemCountService:
    """Сервис с кешированием для улучшения производительности"""
    
    CACHE_TIMEOUT = getattr(settings, 'ITEMS_COUNT_CACHE_TIMEOUT', 300)  # 5 минут
    CACHE_KEY_PREFIX = 'items_count'
    
    @classmethod
    def get_cache_key(cls, endpoint, user_id=None):
        """Генерирует ключ кеша"""
        user_suffix = f"_user_{user_id}" if user_id else "_anonymous"
        return f"{cls.CACHE_KEY_PREFIX}_{endpoint.replace('/', '_')}{user_suffix}"
    
    @classmethod
    def get_count_for_endpoint(cls, endpoint, user=None):
        """Получает количество с кешированием"""
        cache_key = cls.get_cache_key(endpoint, user.id if user else None)
        
        # Пытаемся получить из кеша
        cached_result = cache.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # Если нет в кеше, получаем из сервиса
        result = ItemCountService.get_count_for_endpoint(endpoint, user)
        
        # Кешируем результат
        cache.set(cache_key, json.dumps(result), cls.CACHE_TIMEOUT)
        
        return result
    
    @classmethod
    def get_all_counts(cls, user=None):
        """Получает все количества с кешированием"""
        cache_key = f"{cls.CACHE_KEY_PREFIX}_all_user_{user.id if user else 'anonymous'}"
        
        # Пытаемся получить из кеша
        cached_result = cache.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # Если нет в кеше, получаем из сервиса
        result = ItemCountService.get_all_counts(user)
        
        # Кешируем результат
        cache.set(cache_key, json.dumps(result), cls.CACHE_TIMEOUT)
        
        return result
    
    @classmethod
    def clear_cache(cls, endpoint=None, user=None):
        """Очищает кеш"""
        if endpoint:
            cache_key = cls.get_cache_key(endpoint, user.id if user else None)
            cache.delete(cache_key)
        else:
            # Очищаем весь кеш для пользователя
            cache_pattern = f"{cls.CACHE_KEY_PREFIX}_*_user_{user.id if user else 'anonymous'}"
            # Примечание: для полной очистки по паттерну нужен Redis или Memcached
            cache.clear()


def register_new_endpoint(endpoint, app_name, model_name):
    """Утилита для регистрации нового эндпойнта"""
    ItemCountService.add_endpoint_mapping(endpoint, app_name, model_name)


def get_quick_stats():
    """Быстрая утилита для получения основной статистики"""
    service = ItemCountService()
    stats = service.get_detailed_stats()
    
    return {
        'total_models': stats['summary']['available_models'],
        'total_records': stats['summary']['total_records'],
        'errors': stats['summary']['errors']
    }
