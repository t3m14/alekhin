from django.apps import AppConfig

class ServicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'services'
    
    def ready(self):
        import watson
        from .models import Service
        
        watson.search.register(Service, fields=('name', 'description', 'service_type', 'service_direction'))