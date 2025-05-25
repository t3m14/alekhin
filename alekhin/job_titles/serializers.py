from rest_framework import serializers
from .models import JobTitle


class JobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTitle
        fields = ['id', 'name']
        read_only_fields = ['id']

    def validate_name(self, value):
        """Валидация названия должности"""
        if not value or not value.strip():
            raise serializers.ValidationError("Название должности не может быть пустым")
        
        # Проверяем уникальность при создании или обновлении
        instance = getattr(self, 'instance', None)
        if JobTitle.objects.filter(name__iexact=value.strip()).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError("Должность с таким названием уже существует")
        
        return value.strip()


class JobTitleCreateSerializer(JobTitleSerializer):
    """Сериализатор для создания должности"""
    pass


class JobTitleUpdateSerializer(JobTitleSerializer):
    """Сериализатор для обновления должности"""
    name = serializers.CharField(max_length=255, required=False)