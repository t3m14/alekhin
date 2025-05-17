from django.urls import path
from . import views

urlpatterns = [
    path('services/', views.ServiceViewSet.as_view({'get': 'list', 'post': 'create'}), name='service-list'),
    path('services/<slug:slug>/', views.ServiceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='service-detail'),
]

