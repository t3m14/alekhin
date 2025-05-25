from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import ServiceType
from .serializers import (
    ServiceTypeSerializer, 
    ServiceTypeCreateSerializer, 
    ServiceTypeUpdateSerializer
)
from .permissions import ServiceTypePermission


class ServiceTypeViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.all()
    permission_classes = [ServiceTypePermission]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ServiceTypeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ServiceTypeUpdateSerializer
        return ServiceTypeSerializer
    
    @swagger_auto_schema(
        operation_description="Получение списка всех типов услуг",
        responses={
            200: ServiceTypeSerializer(many=True)
        },
        tags=['Service Types']
    )
    def list(self, request, *args, **kwargs):
        """Получение списка всех типов услуг (доступно без токена)"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @swagger_auto_schema(
        operation_description="Получение типа услуги по ID",
        responses={
            200: ServiceTypeSerializer,
            404: "Тип услуги не найден"
        },
        tags=['Service Types']
    )
    def retrieve(self, request, *args, **kwargs):
        """Получение типа услуги по ID (доступно без токена)"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"error": "Тип услуги не найден"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        operation_description="Создание нового типа услуги (требует токен)",
        request_body=ServiceTypeCreateSerializer,
        responses={
            201: ServiceTypeSerializer,
            400: "Ошибка валидации",
            401: "Требуется аутентификация"
        },
        tags=['Service Types'],
        security=[{'Bearer': []}]
    )
    def create(self, request, *args, **kwargs):
        """Создание нового типа услуги (требует токен)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        response_serializer = ServiceTypeSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_description="Полное обновление типа услуги (требует токен)",
        request_body=ServiceTypeUpdateSerializer,
        responses={
            200: ServiceTypeSerializer,
            400: "Ошибка валидации",
            401: "Требуется аутентификация",
            404: "Тип услуги не найден"
        },
        tags=['Service Types'],
        security=[{'Bearer': []}]
    )
    def update(self, request, *args, **kwargs):
        """Полное обновление типа услуги (требует токен)"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            response_serializer = ServiceTypeSerializer(instance)
            return Response(response_serializer.data)
        except Http404:
            return Response(
                {"error": "Тип услуги не найден"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        operation_description="Частичное обновление типа услуги (требует токен)",
        request_body=ServiceTypeUpdateSerializer,
        responses={
            200: ServiceTypeSerializer,
            400: "Ошибка валидации",
            401: "Требуется аутентификация",
            404: "Тип услуги не найден"
        },
        tags=['Service Types'],
        security=[{'Bearer': []}]
    )
    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление типа услуги (требует токен)"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            response_serializer = ServiceTypeSerializer(instance)
            return Response(response_serializer.data)
        except Http404:
            return Response(
                {"error": "Тип услуги не найден"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        operation_description="Удаление типа услуги (требует токен)",
        responses={
            204: "Тип услуги успешно удален",
            401: "Требуется аутентификация",
            404: "Тип услуги не найден"
        },
        tags=['Service Types'],
        security=[{'Bearer': []}]
    )
    def destroy(self, request, *args, **kwargs):
        """Удаление типа услуги (требует токен)"""
        try:
            instance = self.get_object()
            instance.delete()
            return Response(
                {"message": "Тип услуги успешно удален"}, 
                status=status.HTTP_204_NO_CONTENT
            )
        except Http404:
            return Response(
                {"error": "Тип услуги не найден"}, 
                status=status.HTTP_404_NOT_FOUND
            )