from rest_framework import serializers
from .models import BingoSpace, CustomBingoItem, ProvidedBingoItem, ToDo

class BingoSpaceSerializer(serializers.ModelSerializer):
    class Meta: 
        model = BingoSpace
        fields = "__all__"

class CustomBingoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomBingoItem
        fields = "__all__"

class ProvidedBingoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProvidedBingoItem
        fields = "__all__"

class ToDoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDo
        fields = "__all__"
