# alekhin/goods/serializers.py
# Обновленные сериализаторы для модели Good с необязательным полем article

from rest_framework import serializers
from .models import Good
from images.serializers import ImageSerializer


class GoodCreateSerializer(serializers.ModelSerializer):
    image = serializers.CharField(allow_null=True, required=False)
    article = serializers.CharField(max_length=100, allow_blank=True, allow_null=True, required=False)
    
    class Meta:
        model = Good
        fields = [
            'name', 'image', 'service_direction', 'article', 'price', 
            'description', 'sizes', 'product_care', 'important', 
            'contraindications', 'enabled'
        ]
    
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Название товара не может быть пустым")
        return value.strip()
    
    def validate_article(self, value):
        if value is None or value == "":
            return None
        return str(value).strip()
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Цена не может быть отрицательной")
        return value
    
    def validate_service_direction(self, value):
        if value <= 0:
            raise serializers.ValidationError("ID направления услуги должен быть положительным числом")
        return value


class GoodSerializer(serializers.ModelSerializer):
    image = serializers.CharField(allow_null=True, required=False)
    article = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    
    class Meta:
        model = Good
        fields = [
            'id', 'name', 'image', 'service_direction', 'article', 
            'price', 'description', 'sizes', 'product_care', 'important', 
            'contraindications', 'slug', 'enabled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class GoodUpdateSerializer(serializers.ModelSerializer):
    image = serializers.CharField(allow_null=True, required=False)
    article = serializers.CharField(max_length=100, allow_blank=True, allow_null=True, required=False)
    
    class Meta:
        model = Good
        fields = [
            'name', 'image', 'service_direction', 'article', 'price', 
            'description', 'sizes', 'product_care', 'important', 
            'contraindications', 'enabled'
        ]
    
    def validate_name(self, value):
        if value is not None and (not value or not value.strip()):
            raise serializers.ValidationError("Название товара не может быть пустым")
        return value.strip() if value else value
    
    def validate_article(self, value):
        if value is None or value == "":
            return None
        return str(value).strip()
        
    def validate_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Цена не может быть отрицательной")
        return value


class GoodListSerializer(serializers.ModelSerializer):
    image = serializers.CharField(allow_null=True, required=False)
    article = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    
    class Meta:
        model = Good
        fields = [
            'id', 'name', 'image', 'service_direction', 'article', 'price', 
            'description', 'sizes', 'product_care', 'important', 
            'contraindications', 'enabled', 'slug'
        ]