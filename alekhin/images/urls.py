from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet

urlpatterns = [
    path('', ImageViewSet.as_view({'get': 'list', 'post': 'create'}), name='image-list'),
    path('<int:id>/', ImageViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='image-detail'),
    path('slug/', ImageViewSet.as_view({'get': 'retrieve_by_slug', 'delete': 'destroy'}), name='image-detail-by-slug'),

]