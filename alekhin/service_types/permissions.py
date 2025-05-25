from rest_framework.permissions import BasePermission


class ServiceTypePermission(BasePermission):
    """
    Разрешения для типов услуг:
    - GET запросы доступны всем
    - POST, PUT, PATCH, DELETE требуют аутентификации
    """
    
    def has_permission(self, request, view):
        # GET запросы доступны всем
        if request.method == 'GET':
            return True
        
        # Остальные методы требуют аутентификации
        return request.user and request.user.is_authenticated