from rest_framework import serializers
from .models import Information, InformationImage


# 정보글 이미지 시리얼라이저
class InformationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformationImage
        fields = ['image']


# 정보글 시리얼라이저
class InformationSerializer(serializers.ModelSerializer):
    images = InformationImageSerializer(many=True)
    id = serializers.ReadOnlyField()

    class Meta:
        model = Information
        fields = ['id', 'title', 'content', 'large_category', 'images']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        user = self.context['request'].user
        information = Information.objects.create(user=user, **validated_data)
        for image_data in images_data:
            InformationImage.objects.create(information=information, **image_data)
        return information
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.large_category = validated_data.get('large_category', instance.large_category)