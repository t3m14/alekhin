from django.urls import path
from . import views

urlpatterns = [
    path('', views.SpecialistViewSet.as_view({'get': 'list', 'post': 'create'}), name='specialist-list'),
    path('<int:pk>/', views.SpecialistViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='specialist-detail'),
]