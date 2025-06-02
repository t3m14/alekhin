from rest_framework import serializers
from .models import Test


class TestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = [
            'name', 'service_direction', 'price', 'nomenclature', 'method', 
            'time', 'characteristic', 'rules', 'readings', 'contraindications', 
            'depends_to', 'enabled'
        ]
    
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Название анализа не может быть пустым")
        return value.strip()
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Стоимость не может быть отрицательной")
        return value
    
    def validate_service_direction(self, value):
        if value <= 0:
            raise serializers.ValidationError("ID направления услуги должен быть положительным числом")
        return value


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = [
            'id', 'name', 'service_direction', 'price', 'nomenclature', 'method', 
            'time', 'characteristic', 'rules', 'readings', 'contraindications', 
            'depends_to', 'enabled', 'slug', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class TestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = [
            'name', 'service_direction', 'price', 'nomenclature', 'method', 
            'time', 'characteristic', 'rules', 'readings', 'contraindications', 
            'depends_to', 'enabled'
        ]
    
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Название анализа не может быть пустым")
        return value.strip()
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Стоимость не может быть отрицательной")
        return value


class TestListSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для списка анализов"""
    class Meta:
        model = Test
        fields =['id', 'name', 'service_direction', 'price', 'nomenclature', 'method', 
            'time', 'characteristic', 'rules', 'readings', 'contraindications', 
            'depends_to', 'enabled', 'slug', 'created_at', 'updated_at'
        ]
from rest_framework import serializers
from .models import Test


class TestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = [
            'name', 'service_direction', 'price', 'nomenclature', 'method', 
            'time', 'characteristic', 'rules', 'readings', 'contraindications', 
            'depends_to', 'enabled'
        ]
    
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Название анализа не может быть пустым")
        return value.strip()
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Стоимость не может быть отрицательной")
        return value
    
    def validate_service_direction(self, value):
        if value <= 0:
            raise serializers.ValidationError("ID направления услуги должен быть положительным числом")
        return value


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = [
            'id', 'name', 'service_direction', 'price', 'nomenclature', 'method', 
            'time', 'characteristic', 'rules', 'readings', 'contraindications', 
            'depends_to', 'enabled', 'slug', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class TestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = [
            'name', 'service_direction', 'price', 'nomenclature', 'method', 
            'time', 'characteristic', 'rules', 'readings', 'contraindications', 
            'depends_to', 'enabled'
        ]
    
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Название анализа не может быть пустым")
        return value.strip()
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Стоимость не может быть отрицательной")
        return value


class TestListSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для списка анализов"""
    class Meta:
        model = Test
        fields = ['id', 'name', 'service_direction', 'price', 'nomenclature', 'method', 
            'time', 'characteristic', 'rules', 'readings', 'contraindications', 
            'depends_to', 'enabled', 'slug', 'created_at', 'updated_at'
        ]