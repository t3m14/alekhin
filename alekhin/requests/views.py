from django.db.models import Q
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from .models import Request
from .serializers import RequestCreateSerializer, RequestSerializer, RequestUpdateSerializer
from .filters import RequestFilter


class RequestViewSet(viewsets.ModelViewSet):
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'phone', 'service_name', 'description']
    filterset_class = RequestFilter
    ordering_fields = ['created_at', 'name', 'is_new']
    ordering = ['-created_at']
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_permissions(self):
        if self.action == 'create':
            return []  # create доступен всем (без токена)
        return [IsAuthenticated()]  # все остальные действия требуют токен

    def get_serializer_class(self):
        if self.action == 'create':
            return RequestCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return RequestUpdateSerializer
        return RequestSerializer

    def get_queryset(self):
        queryset = Request.objects.all().select_related('specialist')
        
        # Smart search
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(service_name__icontains=search_query) |
                Q(service_direction__icontains=search_query) |
                Q(service_type__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(specialist__name__icontains=search_query)
            ).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        """
        GET /requests - получение списка заявок с токеном
        Возвращает заявки и добавляет в заголовки общее количество
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Получаем общее количество заявок (до пагинации)
        total_count = queryset.count()
        new_count = queryset.filter(is_new=True).count()
        
        # Применяем пагинацию если она настроена
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)
        
        # Добавляем счетчики в заголовки
        response['Total-Count'] = str(total_count)
        response['New-Count'] = str(new_count)
        response['Access-Control-Expose-Headers'] = 'Total-Count, New-Count'
        
        return response

    def create(self, request, *args, **kwargs):
        """
        POST /requests - создание заявки без токена
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        # Здесь можно добавить отправку email уведомления
        # self.send_notification_email(instance)
        
        return Response(
            RequestSerializer(instance).data, 
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """
        PUT/PATCH /requests/{id} - обновление заявки (требует токен)
        Обычно используется для изменения статуса is_new
        """
        return super().update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        GET /requests/{id} - получение конкретной заявки (требует токен)
        """
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE /requests/{id} - удаление заявки (требует токен)
        """
        return super().destroy(request, *args, **kwargs)
    
    # def send_notification_email(self, request_instance):
    #     """Отправка уведомления на email при создании заявки"""
    #     # Реализация отправки email
    #     pass
