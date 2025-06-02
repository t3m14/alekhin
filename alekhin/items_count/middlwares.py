from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from .utils import CachedItemCountService
import re


class ItemCountCacheMiddleware(MiddlewareMixin):
    """
    Middleware для автоматической очистки кеша при изменении данных
    """
    
    # Паттерны URL, которые могут изменять данные
    CACHE_INVALIDATION_PATTERNS = [
        r'^/api/specialists/',
        r'^/api/images/',
        r'^/api/services/',
        r'^/api/job_titles/',
        r'^/api/tests/',
        r'^/api/goods/',
        r'^/api/service_types/',
        r'^/api/requests/',
    ]
    
    def process_response(self, request, response):
        # Проверяем, был ли это запрос, который мог изменить данные
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Проверяем, соответствует ли URL одному из паттернов
            for pattern in self.CACHE_INVALIDATION_PATTERNS:
                if re.match(pattern, request.path):
                    # Очищаем кеш
                    CachedItemCountService.clear_cache()
                    break
        
        return response
