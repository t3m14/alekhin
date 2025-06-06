from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestViewSet

router = DefaultRouter()
router.register(r'', TestViewSet, basename='test')

urlpatterns = [
    path('', include(router.urls)),
]
