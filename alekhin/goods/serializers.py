from rest_framework import serializers
from .models import Good
from images.serializers import ImageSerializer


class GoodCreateSerializer(serializers.ModelSerializer):
    image = serializers.CharField(allow_null=True)
    
    class Meta:
        model = Good
        fields = [
            'name', 'image', 'service_direction', 'article', 'price', 
            'description', 'sizes', 'product_care', 'important', 
            'contraindications', 'enabled', 'slug'
        ]
    
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Название товара не может быть пустым")
        return value.strip()
    
    def validate_article(self, value):
        if not value or not str(value).strip():
            raise serializers.ValidationError("Артикул не может быть пустым")
        
        # Проверяем уникальность артикула
        instance = getattr(self, 'instance', None)
        if Good.objects.filter(article=str(value).strip()).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError("Товар с таким артикулом уже существует")
        
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
    image = serializers.CharField(allow_null=True)
    
    class Meta:
        model = Good
        fields = [
            'id', 'name', 'image', 'service_direction', 'article', 
            'price', 'description', 'sizes', 'product_care', 'important', 
            'contraindications', 'slug', 'enabled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class GoodUpdateSerializer(serializers.ModelSerializer):
    image = serializers.CharField(allow_null=True)
    
    class Meta:
        model = Good
        fields = [
            'name', 'image', 'service_direction', 'article', 'price', 
            'description', 'sizes', 'product_care', 'important', 
            'contraindications', 'enabled', 'slug'
        ]
    
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Название товара не может быть пустым")
        return value.strip()
    
    def validate_article(self, value):
        if not value or not str(value).strip():
            raise serializers.ValidationError("Артикул не может быть пустым")
        
        # Проверяем уникальность артикула при обновлении
        instance = getattr(self, 'instance', None)
        if Good.objects.filter(article=str(value).strip()).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError("Товар с таким артикулом уже существует")
        
        return str(value).strip()
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Цена не может быть отрицательной")
        return value


class GoodListSerializer(serializers.ModelSerializer):
    image = serializers.CharField(allow_null=True)
    class Meta:
        model = Good
        fields = [
        'name', 'image', 'service_direction', 'article', 'price', 
        'description', 'sizes', 'product_care', 'important', 
        'contraindications', 'enabled', 'slug'
    ]