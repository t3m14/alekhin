from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import ImageModel
from .serializers import ImageUploadSerializer, ImageSerializer, ImageUpdateSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = ImageModel.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ImageUploadSerializer
        elif self.action in ['update', 'partial_update']:
            return ImageUpdateSerializer
        return ImageSerializer
    
    @swagger_auto_schema(
        operation_description="Загрузка изображения",
        manual_parameters=[
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                description="Файл изображения",
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                'original_filename',
                openapi.IN_FORM,
                description="Оригинальное имя файла",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'crop',
                openapi.IN_FORM,
                description="Создать обрезанную версию для мобильных устройств",
                type=openapi.TYPE_BOOLEAN,
                required=False
            ),
        ],
        responses={
            201: ImageSerializer,
            400: "Ошибка валидации"
        }
    )
    def create(self, request, *args, **kwargs):
        """Загрузка нового изображения с возможностью обрезки"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        # Возвращаем полную информацию об изображении
        response_serializer = ImageSerializer(instance, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_description="Получение изображения по ID",
        responses={
            200: ImageSerializer,
            404: "Изображение не найдено"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Получение изображения по ID"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"error": "Изображение не найдено"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        operation_description="Получение списка всех изображений",
        responses={200: ImageSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """Получение списка всех изображений"""
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Обновление информации об изображении",
        responses={
            200: ImageSerializer,
            404: "Изображение не найдено"
        }
    )
    def update(self, request, *args, **kwargs):
        """Обновление информации об изображении"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Возвращаем полную информацию
        response_serializer = ImageSerializer(instance, context={'request': request})
        return Response(response_serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление информации об изображении"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Удаление изображения",
        responses={
            204: "Изображение успешно удалено",
            404: "Изображение не найдено"
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Удаление изображения"""
        try:
            slug = request.query_params.get('slug', None)
            if not slug:
                 return Response(
                    {"error": "Слаг не указан"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            instance = ImageModel.objects.get(image=slug.split('media/')[-1])
            
            # Удаляем файлы с диска
            if instance.image:
                instance.image.delete(save=False)
            if instance.cropped_image:
                instance.cropped_image.delete(save=False)
                
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ImageModel.DoesNotExist:
            return Response(
                {"error": "Изображение не найдено"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def retrieve_by_slug(self, request, *args, **kwargs):
        """Получение изображения по слагу"""
        # получтиь слаг из тела запроса
        slug = request.data.get('slug', None)
        if not slug:
            return Response(
                {"error": "Слаг не указан"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            instance = ImageModel.objects.get(image=slug.split('media/')[-1])
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except ImageModel.DoesNotExist:
            return Response(
                {"error": "Изображение не найдено"}, 
                status=status.HTTP_404_NOT_FOUND
            )