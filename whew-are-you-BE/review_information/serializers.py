from rest_framework import serializers
from .models import Information, InformationImage

class InformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Information
        fields = ['title', 'content', 'large_category']

class InformationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformationImage
        fields = ['id']