from django.urls import path
from . import views

urlpatterns = [
    path('', views.SpecialistViewSet.as_view({'get': 'list', 'post': 'create'}), name='specialist-list'),
]