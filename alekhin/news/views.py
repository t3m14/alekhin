# alekhin/news/views.py
from django.db.models import Q
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from rest_framework.pagination import PageNumberPagination
from .models import News
from .serializers import (
    NewsCreateSerializer, NewsSerializer, NewsUpdateSerializer, NewsListSerializer
)
from .filters import NewsFilter


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class NewsViewSet(viewsets.ModelViewSet):
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'text']
    filterset_class = NewsFilter
    ordering_fields = ['created_at', 'title', 'time_to_read', 'service_direction']
    ordering = ['-created_at']
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return []  # GET запросы доступны всем (без токена)
        return [IsAuthenticated()]  # остальные действия требуют токен

    def get_serializer_class(self):
        if self.action == 'create':
            return NewsCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return NewsUpdateSerializer
        elif self.action == 'list':
            return NewsListSerializer
        return NewsSerializer

    def get_queryset(self):
        queryset = News.objects.all()
        
        # Для неаутентифицированных пользователей показываем только активные статьи
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(enabled=True)
        
        # Smart search
        search_query = self.request.query_params.get('search', None)
        if search_query:
            search_query = search_query.strip().lower()
            queryset = queryset.filter(
                Q(title__unaccent__lower__trigram_similar=search_query) |
                Q(text__unaccent__lower__trigram_similar=search_query)
            ).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        """GET /news - получение списка статей"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Фильтр по service_direction
        service_direction = self.request.query_params.get('service_direction', None)
        if service_direction:
            queryset = queryset.filter(service_direction=str(service_direction))
        
        # Получаем общее количество статей
        total_count = queryset.count()
        enabled_count = queryset.filter(enabled=True).count()
        
        # Применяем пагинацию
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            # Переименовываем поле count в items_count
            response.data['items_count'] = response.data.pop('count')
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response({
                'results': serializer.data,
                'items_count': total_count
            })
        
        # Добавляем счетчики в заголовки
        response['Total-Count'] = str(total_count)
        response['Enabled-Count'] = str(enabled_count)
        response['Access-Control-Expose-Headers'] = 'Total-Count, Enabled-Count'
        
        return response

    def create(self, request, *args, **kwargs):
        """POST /news - создание статьи (требует токен)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        return Response(
            NewsSerializer(instance).data, 
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, *args, **kwargs):
        """GET /news/{slug} - получение конкретной статьи"""
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """PUT/PATCH /news/{slug} - обновление статьи (требует токен)"""
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """DELETE /news/{slug} - удаление статьи (требует токен)"""
        return super().destroy(request, *args, **kwargs)