from rest_framework import serializers
from .models import Request
from specialists.models import Specialist


class RequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = [
            'name', 'email', 'phone', 'is_service', 'is_goods', 'is_analysis',
            'service_name', 'service_direction', 'service_type', 'specialist',
            'additional_info', 'description'
        ]
    
    def validate(self, data):
        # Проверяем, что выбран хотя бы один тип заявки
        # if not any([data.get('is_service'), data.get('is_goods'), data.get('is_analysis')]):
        #     raise serializers.ValidationError("Необходимо выбрать хотя бы один тип заявки")
        
        # Если выбрана услуга, проверяем обязательные поля
        if data.get('is_service') and not data.get('service_name'):
            raise serializers.ValidationError("Для медицинской услуги необходимо указать название")
        
        return data
    
    # def validate_email(self, value):
    #     if not value or not value.strip():
    #         raise serializers.ValidationError("Email не может быть пустым")
    #     return value.strip()
    def validate_phone(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Телефон не может быть пустым")
        return value.strip()
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Имя не может быть пустым")
        return value.strip()


class RequestSerializer(serializers.ModelSerializer):
    specialist_name = serializers.CharField(source='specialist.name', read_only=True)
    
    class Meta:
        model = Request
        fields = [
            'id', 'name', 'email', 'phone', 'is_service', 'is_goods', 'is_analysis',
            'service_name', 'service_direction', 'service_type', 'specialist', 'specialist_name',
            'additional_info', 'description', 'created_at', 'is_new'
        ]
        read_only_fields = ['id', 'created_at']


class RequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['is_new', 'description']
