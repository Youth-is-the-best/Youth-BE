from rest_framework import serializers
from .models import Information, InformationImage


# 정보글 이미지 시리얼라이저
class InformationImageSerializer(serializers.ModelSerializer):
    image_id = serializers.IntegerField(source='id')

    class Meta:
        model = InformationImage
        fields = ['image_id', 'image']


# 정보글 GET 시리얼라이저
class InformationGETSerializer(serializers.ModelSerializer):
    information_id = serializers.IntegerField(source='id')
    images = InformationImageSerializer(many=True, read_only=True)

    class Meta:
        model = Information
        fields = ['information_id', 'title', 'content', 'large_category', 'images']


# 정보글 POST 시리얼라이저
class InformationSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Information
        fields = ['id', 'title', 'content', 'large_category']

    def create(self, validated_data):
        title = validated_data['title']
        content = validated_data['content']
        large_category = validated_data['large_category']
        images = self.context['request'].FILES.getlist('images')

        information = Information(title=title, content=content, large_category=large_category)
        information.save()
        for image in images:
            image_data = InformationImage(information=information, image=image)
            image_data.save()
        validated_data['images'] = images
        return validated_data
    
    def update(self, instance, validated_data):
        images_data = self.context['request'].FILES.getlist('images')
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.large_category = validated_data.get('large_category', instance.large_category)
        instance.save()

        if images_data is not None:
            # Clear existing images if any
            instance.images.all().delete()
            for image_data in images_data:
                InformationImage.objects.create(information=instance, image=image_data)

        return instance