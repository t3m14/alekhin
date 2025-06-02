from django.apps import apps
from django.db import models
from django.core.exceptions import ImproperlyConfigured
import importlib


class ItemCountService:
    """Сервис для подсчета записей в различных приложениях"""
    
    # Маппинг эндпойнтов к моделям
    ENDPOINT_MODEL_MAPPING = {
        '/specialists/': ('specialists', 'Specialist'),
        '/images/': ('images', 'Image'),
        '/services/': ('services', 'Service'),
        '/job_titles/': ('job_titles', 'JobTitle'),
        '/tests/': ('tests', 'Test'),
        '/goods/': ('goods', 'Good'),
        '/requests/': ('requests', 'Request'),
        # Можно легко добавлять новые эндпойнты
    }
    
    @classmethod
    def get_model_from_endpoint(cls, endpoint):
        """Получает модель по эндпойнту"""
        if endpoint not in cls.ENDPOINT_MODEL_MAPPING:
            return None
        
        app_name, model_name = cls.ENDPOINT_MODEL_MAPPING[endpoint]
        
        try:
            return apps.get_model(app_name, model_name)
        except LookupError:
            return None
    
    @classmethod
    def get_count_for_endpoint(cls, endpoint, user=None):
        """Получает количество записей для конкретного эндпойнта"""
        model = cls.get_model_from_endpoint(endpoint)
        
        if not model:
            return {
                'endpoint': endpoint,
                'count': 0,
                'error': 'Endpoint not found or model not available'
            }
        
        try:
            queryset = model.objects.all()
            
            # Применяем фильтры в зависимости от модели и пользователя
            queryset = cls._apply_filters(queryset, model, user)
            
            count = queryset.count()
            
            return {
                'endpoint': endpoint,
                'count': count,
                'model': f"{model._meta.app_label}.{model._meta.model_name}",
                'error': None
            }
            
        except Exception as e:
            return {
                'endpoint': endpoint,
                'count': 0,
                'error': str(e)
            }
    
    @classmethod
    def _apply_filters(cls, queryset, model, user):
        """Применяет фильтры в зависимости от модели и пользователя"""
        model_name = model._meta.model_name
        
        # Если пользователь не аутентифицирован, применяем ограничения
        if not user or not user.is_authenticated:
            # Для специалистов показываем только надежных
            if model_name == 'specialist' and hasattr(model, 'is_reliable'):
                queryset = queryset.filter(is_reliable=True)
            
            # Для товаров, анализов и услуг показываем только активные
            elif hasattr(model, 'enabled'):
                queryset = queryset.filter(enabled=True)
        
        return queryset
    
    @classmethod
    def get_all_counts(cls, user=None):
        """Получает количество записей для всех эндпойнтов"""
        results = {}
        
        for endpoint in cls.ENDPOINT_MODEL_MAPPING.keys():
            results[endpoint] = cls.get_count_for_endpoint(endpoint, user)
        
        return results
    
    @classmethod
    def get_available_endpoints(cls):
        """Возвращает список доступных эндпойнтов"""
        return list(cls.ENDPOINT_MODEL_MAPPING.keys())
    
    @classmethod
    def add_endpoint_mapping(cls, endpoint, app_name, model_name):
        """Динамически добавляет новый эндпойнт"""
        cls.ENDPOINT_MODEL_MAPPING[endpoint] = (app_name, model_name)
    
    @classmethod
    def get_detailed_stats(cls, user=None):
        """Получает детальную статистику по всем моделям"""
        stats = {
            'total_endpoints': len(cls.ENDPOINT_MODEL_MAPPING),
            'endpoints': {},
            'summary': {
                'total_records': 0,
                'available_models': 0,
                'errors': 0
            }
        }
        
        for endpoint in cls.ENDPOINT_MODEL_MAPPING.keys():
            result = cls.get_count_for_endpoint(endpoint, user)
            stats['endpoints'][endpoint] = result
            
            if result['error']:
                stats['summary']['errors'] += 1
            else:
                stats['summary']['total_records'] += result['count']
                stats['summary']['available_models'] += 1
        
        return stats
