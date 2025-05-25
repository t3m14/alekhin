from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet

router = DefaultRouter()
router.register(r'', ImageViewSet, basename='images')

urlpatterns = [
    path('', include(router.urls)),
]