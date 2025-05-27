from django.db.models import Q
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from .models import Good
from .serializers import (
    GoodCreateSerializer, GoodSerializer, GoodUpdateSerializer, GoodListSerializer
)
from .filters import GoodFilter


class GoodViewSet(viewsets.ModelViewSet):
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'name', 'article', 'description', 'sizes', 'product_care', 
        'important', 'contraindications'
    ]
    filterset_class = GoodFilter
    ordering_fields = ['created_at', 'name', 'price', 'article', 'service_direction']
    ordering = ['-created_at']
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return []  # GET запросы доступны всем (без токена)
        return [IsAuthenticated()]  # остальные действия требуют токен

    def get_serializer_class(self):
        if self.action == 'create':
            return GoodCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return GoodUpdateSerializer
        elif self.action == 'list':
            return GoodListSerializer
        return GoodSerializer

    def get_queryset(self):
        queryset = Good.objects.all().select_related('image')
        
        # Для неаутентифицированных пользователей показываем только активные товары
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(enabled=True)
        
        # Smart search
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(article__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(sizes__icontains=search_query) |
                Q(product_care__icontains=search_query) |
                Q(important__icontains=search_query) |
                Q(contraindications__icontains=search_query)
            ).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        """GET /goods - получение списка товаров"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Получаем общее количество товаров
        total_count = queryset.count()
        enabled_count = queryset.filter(enabled=True).count()
        
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
        response['Enabled-Count'] = str(enabled_count)
        response['Access-Control-Expose-Headers'] = 'Total-Count, Enabled-Count'
        
        return response

    def create(self, request, *args, **kwargs):
        """POST /goods - создание товара (требует токен)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        return Response(
            GoodSerializer(instance).data, 
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, *args, **kwargs):
        """GET /goods/{slug} - получение конкретного товара"""
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """PUT/PATCH /goods/{slug} - обновление товара (требует токен)"""
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """DELETE /goods/{slug} - удаление товара (требует токен)"""
        return super().destroy(request, *args, **kwargs)
