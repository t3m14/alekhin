# alekhin/news/serializers.py
from rest_framework import serializers
from .models import News


class NewsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = [
            'title', 'text', 'image', 'time_to_read', 
            'service_direction', 'enabled'
        ]
    
    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Заголовок статьи не может быть пустым")
        return value.strip()
    
    def validate_text(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Текст статьи не может быть пустым")
        return value.strip()
    
    def validate_time_to_read(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError("Время чтения должно быть больше 0")
        return value
    
    def validate_service_direction(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("ID направления услуги должен быть положительным числом")
        return value


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = [
            'id', 'title', 'text', 'image', 'time_to_read', 
            'service_direction', 'slug', 'enabled', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class NewsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = [
            'title', 'text', 'image', 'time_to_read', 
            'service_direction', 'enabled'
        ]
    
    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Заголовок статьи не может быть пустым")
        return value.strip()
    
    def validate_text(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Текст статьи не может быть пустым")
        return value.strip()
    
    def validate_time_to_read(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError("Время чтения должно быть больше 0")
        return value


class NewsListSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для списка статей"""
    class Meta:
        model = News
        fields = [
            'id', 'title', 'image', 'time_to_read', 
            'service_direction', 'slug', 'enabled', 'created_at'
        ]