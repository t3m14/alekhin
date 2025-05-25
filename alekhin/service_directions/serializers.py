from rest_framework import serializers
from .models import ServiceDirection

class ServiceDirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceDirection
        fields = ['id', 'name', 'types', 'questions_answers']
        read_only_fields = ['id']