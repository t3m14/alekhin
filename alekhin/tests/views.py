from django.db.models import Q
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from .models import Test
from .serializers import (
    TestCreateSerializer, TestSerializer, TestUpdateSerializer, TestListSerializer
)
from .filters import TestFilter


class TestViewSet(viewsets.ModelViewSet):
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'name', 'nomenclature', 'method', 'characteristic', 'rules', 
        'readings', 'contraindications', 'depends_to'
    ]
    filterset_class = TestFilter
    ordering_fields = ['created_at', 'name', 'price', 'service_direction']
    ordering = ['-created_at']
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return []  # GET запросы доступны всем (без токена)
        return [IsAuthenticated()]  # остальные действия требуют токен

    def get_serializer_class(self):
        if self.action == 'create':
            return TestCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TestUpdateSerializer
        elif self.action == 'list':
            return TestListSerializer
        return TestSerializer

    def get_queryset(self):
        queryset = Test.objects.all()
        
        # Для неаутентифицированных пользователей показываем только активные анализы
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(enabled=True)
        
        # Smart search
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(nomenclature__icontains=search_query) |
                Q(method__icontains=search_query) |
                Q(characteristic__icontains=search_query) |
                Q(rules__icontains=search_query) |
                Q(readings__icontains=search_query) |
                Q(contraindications__icontains=search_query) |
                Q(depends_to__icontains=search_query)
            ).distinct()
            if not queryset.exists():
                search_query = str(search_query).capitalize()
                queryset = queryset.filter(
                    Q(name__icontains=search_query) |
                    Q(nomenclature__icontains=search_query) |
                    Q(method__icontains=search_query) |
                    Q(characteristic__icontains=search_query) |
                    Q(rules__icontains=search_query) |
                    Q(readings__icontains=search_query) |
                    Q(contraindications__icontains=search_query) |
                    Q(depends_to__icontains=search_query)
                ).distinct()
                if not queryset.exists():
                    search_query = str(search_query).upper()
                    queryset = queryset.filter(
                        Q(name__icontains=search_query) |
                        Q(nomenclature__icontains=search_query) |
                        Q(method__icontains=search_query) |
                        Q(characteristic__icontains=search_query) |
                        Q(rules__icontains=search_query) |
                        Q(readings__icontains=search_query) |
                        Q(contraindications__icontains=search_query) |
                        Q(depends_to__icontains=search_query)
                    ).distinct()
                    if not queryset.exists():
                        search_query = str(search_query).title()
                        queryset = queryset.filter(
                            Q(name__icontains=search_query) |
                            Q(nomenclature__icontains=search_query) |
                            Q(method__icontains=search_query) |
                            Q(characteristic__icontains=search_query) |
                            Q(rules__icontains=search_query) |
                            Q(readings__icontains=search_query) |
                            Q(contraindications__icontains=search_query) |
                            Q(depends_to__icontains=search_query)
                        ).distinct()
                        if not queryset.exists():
                            search_query = str(search_query).lower()
                            queryset = queryset.filter(
                                Q(name__icontains=search_query) |
                                Q(nomenclature__icontains=search_query) |
                                Q(method__icontains=search_query) |
                                Q(characteristic__icontains=search_query) |
                                Q(rules__icontains=search_query) |
                                Q(readings__icontains=search_query) |
                                Q(contraindications__icontains=search_query) |
                                Q(depends_to__icontains=search_query)
                            ).distinct()
        return queryset

    def list(self, request, *args, **kwargs):
        """GET /tests - получение списка анализов"""
        queryset = self.filter_queryset(self.get_queryset())
        service_direction = self.request.query_params.get('service_direction', None)
        # Получаем общее количество анализов
        if service_direction:
            queryset = queryset.filter(service_direction=str(service_direction))
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
        """POST /tests - создание анализа (требует токен)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        return Response(
            TestSerializer(instance).data, 
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, *args, **kwargs):
        """GET /tests/{slug} - получение конкретного анализа"""
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """PUT/PATCH /tests/{slug} - обновление анализа (требует токен)"""
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """DELETE /tests/{slug} - удаление анализа (требует токен)"""
        return super().destroy(request, *args, **kwargs)
