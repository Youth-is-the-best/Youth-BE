from rest_framework import serializers
from .models import BingoSpace, CustomBingoItem, ProvidedBingoItem

class BingoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomBingoItem
        fields = "__all__"
