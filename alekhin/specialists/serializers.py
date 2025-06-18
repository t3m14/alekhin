# alekhin/specialists/serializers.py
# Обновленный сериализатор для модели Specialist

from rest_framework import serializers
from .models import Specialist


class SpecialistCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания специалиста"""
    
    class Meta:
        model = Specialist
        fields = [
            'name', 'image', 'directions', 'titles', 'experience',
            'is_reliable', 'degree', 'biography', 'serts'
        ]
    
    def validate_name(self, value):
        """Валидация имени специалиста"""
        if not value or not value.strip():
            raise serializers.ValidationError("Имя специалиста не может быть пустым")
        return value.strip()
    
    def validate_image(self, value):
        """Валидация изображения"""
        if not value or not value.strip():
            raise serializers.ValidationError("Изображение специалиста обязательно")
        return value.strip()
    
    def validate_experience(self, value):
        """Валидация опыта работы"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Опыт работы не может быть отрицательным")
        return value


class SpecialistSerializer(serializers.ModelSerializer):
    """Основной сериализатор для специалиста"""
    
    class Meta:
        model = Specialist
        fields = [
            'id', 'name', 'image', 'directions', 'titles', 'experience',
            'is_reliable', 'degree', 'biography', 'serts'
        ]
        read_only_fields = ['id']


class SpecialistUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления специалиста"""
    
    class Meta:
        model = Specialist
        fields = [
            'name', 'image', 'directions', 'titles', 'experience',
            'is_reliable', 'degree', 'biography', 'serts'
        ]
        
    def validate_name(self, value):
        if value is not None and (not value or not value.strip()):
            raise serializers.ValidationError("Имя специалиста не может быть пустым")
        return value.strip() if value else value
    
    def validate_image(self, value):
        if value is not None and (not value or not value.strip()):
            raise serializers.ValidationError("Изображение специалиста обязательно")
        return value.strip() if value else value
    
    def validate_experience(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Опыт работы не может быть отрицательным")
        return value


class SpecialistListSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для списка специалистов"""
    
    class Meta:
        model = Specialist
        fields = ['id', 'name', 'image', 'directions', 'experience', 'is_reliable']