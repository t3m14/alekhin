from rest_framework import serializers


class ItemCountRequestSerializer(serializers.Serializer):
    """Сериализатор для запроса количества записей"""
    endpoint = serializers.CharField(
        max_length=255,
        help_text="Эндпойнт для которого нужно получить количество записей (например: /specialists/)"
    )
    
    def validate_endpoint(self, value):
        """Валидация эндпойнта"""
        if not value.startswith('/'):
            value = '/' + value
        if not value.endswith('/'):
            value = value + '/'
        return value


class ItemCountResponseSerializer(serializers.Serializer):
    """Сериализатор для ответа с количеством записей"""
    endpoint = serializers.CharField()
    count = serializers.IntegerField()
    model = serializers.CharField(required=False, allow_null=True)
    error = serializers.CharField(required=False, allow_null=True)


class AllCountsResponseSerializer(serializers.Serializer):
    """Сериализатор для ответа со всеми количествами"""
    def to_representation(self, instance):
        # instance - это словарь с результатами
        return {
            endpoint: ItemCountResponseSerializer(data).data 
            for endpoint, data in instance.items()
        }


class DetailedStatsResponseSerializer(serializers.Serializer):
    """Сериализатор для детальной статистики"""
    total_endpoints = serializers.IntegerField()
    endpoints = serializers.DictField()
    summary = serializers.DictField()


class AvailableEndpointsSerializer(serializers.Serializer):
    """Сериализатор для списка доступных эндпойнтов"""
    endpoints = serializers.ListField(child=serializers.CharField())
    total = serializers.IntegerField()
