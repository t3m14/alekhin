from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .services import ItemCountService
from .serializers import (
    ItemCountRequestSerializer,
    ItemCountResponseSerializer,
    AllCountsResponseSerializer,
    DetailedStatsResponseSerializer,
    AvailableEndpointsSerializer
)


@swagger_auto_schema(
    method='get',
    operation_description="Получить количество записей для всех эндпойнтов",
    responses={
        200: AllCountsResponseSerializer,
        401: "Unauthorized"
    }
)
@swagger_auto_schema(
    method='post',
    operation_description="Получить количество записей для конкретного эндпойнта",
    request_body=ItemCountRequestSerializer,
    responses={
        200: ItemCountResponseSerializer,
        400: "Bad Request",
        401: "Unauthorized"
    }
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def items_count(request):
    """
    Основной эндпойнт для получения количества записей
    
    GET: Возвращает количество записей для всех эндпойнтов
    POST: Возвращает количество записей для конкретного эндпойнта
    """
    
    if request.method == 'GET':
        # Получаем количество для всех эндпойнтов
        results = ItemCountService.get_all_counts(user=request.user)
        
        return Response(results, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Получаем количество для конкретного эндпойнта
        serializer = ItemCountRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        endpoint = serializer.validated_data['endpoint']
        result = ItemCountService.get_count_for_endpoint(endpoint, user=request.user)
        
        return Response(result, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Получить детальную статистику по всем моделям",
    responses={
        200: DetailedStatsResponseSerializer,
        401: "Unauthorized"
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detailed_stats(request):
    """Получить детальную статистику по всем моделям"""
    
    stats = ItemCountService.get_detailed_stats(user=request.user)
    
    return Response(stats, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Получить список всех доступных эндпойнтов",
    responses={
        200: AvailableEndpointsSerializer,
        401: "Unauthorized"
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_endpoints(request):
    """Получить список всех доступных эндпойнтов"""
    
    endpoints = ItemCountService.get_available_endpoints()
    
    response_data = {
        'endpoints': endpoints,
        'total': len(endpoints)
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


# Дополнительные эндпойнты для удобства

@swagger_auto_schema(
    method='get',
    operation_description="Получить количество специалистов",
    responses={200: ItemCountResponseSerializer, 401: "Unauthorized"}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def specialists_count(request):
    """Получить количество специалистов"""
    result = ItemCountService.get_count_for_endpoint('/specialists/', user=request.user)
    return Response(result, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Получить количество изображений",
    responses={200: ItemCountResponseSerializer, 401: "Unauthorized"}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def images_count(request):
    """Получить количество изображений"""
    result = ItemCountService.get_count_for_endpoint('/images/', user=request.user)
    return Response(result, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Получить количество услуг",
    responses={200: ItemCountResponseSerializer, 401: "Unauthorized"}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def services_count(request):
    """Получить количество услуг"""
    result = ItemCountService.get_count_for_endpoint('/services/', user=request.user)
    return Response(result, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Получить количество должностей",
    responses={200: ItemCountResponseSerializer, 401: "Unauthorized"}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_titles_count(request):
    """Получить количество должностей"""
    result = ItemCountService.get_count_for_endpoint('/job_titles/', user=request.user)
    return Response(result, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Получить количество анализов",
    responses={200: ItemCountResponseSerializer, 401: "Unauthorized"}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tests_count(request):
    """Получить количество анализов"""
    result = ItemCountService.get_count_for_endpoint('/tests/', user=request.user)
    return Response(result, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Получить количество товаров",
    responses={200: ItemCountResponseSerializer, 401: "Unauthorized"}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def goods_count(request):
    """Получить количество товаров"""
    result = ItemCountService.get_count_for_endpoint('/goods/', user=request.user)
    return Response(result, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="Получить количество заявок",
    responses={200: ItemCountResponseSerializer, 401: "Unauthorized"}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def requests_count(request):
    """Получить количество заявок"""
    result = ItemCountService.get_count_for_endpoint('/requests/', user=request.user)
    return Response(result, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="Получить количество типов услуг",
    responses={200: ItemCountResponseSerializer, 401: "Unauthorized"}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def service_types_count(request):
    """Получить количество типов услуг"""
    result = ItemCountService.get_count_for_endpoint('/service_types/', user=request.user)
    return Response(result, status=status.HTTP_200_OK)
