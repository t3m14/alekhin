from rest_framework import serializers
from .models import *

class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = [
            'id', 'name', 'price', 'main_image', 'procedure_number',
            'procedure_duration', 'rehab_duration', 'description',
            'service_direction', 'service_type', 'specialists',
            'readings', 'contraindications', 'devices', 'need_to_have',
            'images', 'serts', 'is_popular', 'slug',
            'created_at'
        ]
        read_only_fields = ['created_at']
        extra_kwargs = {
            'slug': {'required': False, 'read_only': True}
        }
        def get_sensensitive_fields(self, obj):
            request = self.context.get('request')
            if request and  hasattr(request, 'user') and request.user.is_authenticated:
                return obj.enabled
            return False