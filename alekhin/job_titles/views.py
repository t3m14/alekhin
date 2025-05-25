from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import JobTitle
from .serializers import (
    JobTitleSerializer, 
    JobTitleCreateSerializer, 
    JobTitleUpdateSerializer
)
from .permissions import JobTitlePermission


class JobTitleViewSet(viewsets.ModelViewSet):
    queryset = JobTitle.objects.all()
    permission_classes = [JobTitlePermission]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return JobTitleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return JobTitleUpdateSerializer
        return JobTitleSerializer
    
    @swagger_auto_schema(
        operation_description="Получение списка всех должностей",
        responses={
            200: JobTitleSerializer(many=True)
        },
        tags=['Job Titles']
    )
    def list(self, request, *args, **kwargs):
        """Получение списка всех должностей (доступно без токена)"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @swagger_auto_schema(
        operation_description="Получение должности по ID",
        responses={
            200: JobTitleSerializer,
            404: "Должность не найдена"
        },
        tags=['Job Titles']
    )
    def retrieve(self, request, *args, **kwargs):
        """Получение должности по ID (доступно без токена)"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"error": "Должность не найдена"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        operation_description="Создание новой должности (требует токен)",
        request_body=JobTitleCreateSerializer,
        responses={
            201: JobTitleSerializer,
            400: "Ошибка валидации",
            401: "Требуется аутентификация"
        },
        tags=['Job Titles'],
        security=[{'Bearer': []}]
    )
    def create(self, request, *args, **kwargs):
        """Создание новой должности (требует токен)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        response_serializer = JobTitleSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_description="Полное обновление должности (требует токен)",
        request_body=JobTitleUpdateSerializer,
        responses={
            200: JobTitleSerializer,
            400: "Ошибка валидации",
            401: "Требуется аутентификация",
            404: "Должность не найдена"
        },
        tags=['Job Titles'],
        security=[{'Bearer': []}]
    )
    def update(self, request, *args, **kwargs):
        """Полное обновление должности (требует токен)"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            response_serializer = JobTitleSerializer(instance)
            return Response(response_serializer.data)
        except Http404:
            return Response(
                {"error": "Должность не найдена"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        operation_description="Частичное обновление должности (требует токен)",
        request_body=JobTitleUpdateSerializer,
        responses={
            200: JobTitleSerializer,
            400: "Ошибка валидации",
            401: "Требуется аутентификация",
            404: "Должность не найдена"
        },
        tags=['Job Titles'],
        security=[{'Bearer': []}]
    )
    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление должности (требует токен)"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            response_serializer = JobTitleSerializer(instance)
            return Response(response_serializer.data)
        except Http404:
            return Response(
                {"error": "Должность не найдена"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        operation_description="Удаление должности (требует токен)",
        responses={
            204: "Должность успешно удалена",
            401: "Требуется аутентификация",
            404: "Должность не найдена"
        },
        tags=['Job Titles'],
        security=[{'Bearer': []}]
    )
    def destroy(self, request, *args, **kwargs):
        """Удаление должности (требует токен)"""
        try:
            instance = self.get_object()
            instance.delete()
            return Response(
                {"message": "Должность успешно удалена"}, 
                status=status.HTTP_204_NO_CONTENT
            )
        except Http404:
            return Response(
                {"error": "Должность не найдена"}, 
                status=status.HTTP_404_NOT_FOUND
            )