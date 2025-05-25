from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobTitleViewSet

router = DefaultRouter()
router.register(r'', JobTitleViewSet, basename='job-titles')

urlpatterns = [
    path('', include(router.urls)),
]