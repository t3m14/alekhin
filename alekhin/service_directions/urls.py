from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceDirectionViewSet

router = DefaultRouter()
router.register(r'', ServiceDirectionViewSet, basename='service-direction')

urlpatterns = [
    path('', include(router.urls)),
]