from rest_framework import serializers
from .models import ImageModel


class ImageUploadSerializer(serializers.ModelSerializer):
    crop = serializers.BooleanField(write_only=True, required=False, default=False)
    
    class Meta:
        model = ImageModel
        fields = ['image', 'original_filename', 'crop']
        
    def create(self, validated_data):
        crop = validated_data.pop('crop', False)
        
        # Получаем оригинальное имя файла если не указано
        if not validated_data.get('original_filename'):
            validated_data['original_filename'] = validated_data['image'].name
            
        # Получаем размер файла
        validated_data['file_size'] = validated_data['image'].size
        
        instance = super().create(validated_data)
        
        # Создаем обрезанную версию если нужно
        if crop:
            instance.create_cropped_version()
            instance.save()
            
        return instance


class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    cropped_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ImageModel
        fields = [
            'id', 'original_filename', 'image_url', 'cropped_image_url',
            'file_size', 'width', 'height', 'created_at', 'updated_at'
        ]
        
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
        
    def get_cropped_image_url(self, obj):
        if obj.cropped_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cropped_image.url)
            return obj.cropped_image.url
        return None


class ImageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ['original_filename']