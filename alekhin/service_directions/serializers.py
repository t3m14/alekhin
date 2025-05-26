from rest_framework import serializers
from .models import ServiceDirection

class ServiceDirectionSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False, read_only=True)
    
    class Meta:
        model = ServiceDirection
        fields = ['id', 'name', 'types', 'questions_answers', 'slug']
        read_only_fields = ['id', 'slug']