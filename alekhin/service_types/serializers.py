from rest_framework import serializers
from .models import ServiceType


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ['id', 'name']
        read_only_fields = ['id']

    def validate_name(self, value):
        """Валидация названия типа услуги"""
        if not value or not value.strip():
            raise serializers.ValidationError("Название типа услуги не может быть пустым")
        
        # Проверяем уникальность при создании или обновлении
        instance = getattr(self, 'instance', None)
        if ServiceType.objects.filter(name__iexact=value.strip()).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError("Тип услуги с таким названием уже существует")
        
        return value.strip()


class ServiceTypeCreateSerializer(ServiceTypeSerializer):
    """Сериализатор для создания типа услуги"""
    pass


class ServiceTypeUpdateSerializer(ServiceTypeSerializer):
    """Сериализатор для обновления типа услуги"""
    name = serializers.CharField(max_length=255, required=False)
