from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import ServiceDirection
from .serializers import ServiceDirectionSerializer
from django.utils.text import slugify

class ServiceDirectionViewSet(viewsets.ModelViewSet):
    queryset = ServiceDirection.objects.all()
    serializer_class = ServiceDirectionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data.get('slug'):
            serializer.validated_data['slug'] = slugify(serializer.validated_data.get('name', ''))
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data.get('slug') and 'name' in serializer.validated_data:
            serializer.validated_data['slug'] = slugify(serializer.validated_data['name'])
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)