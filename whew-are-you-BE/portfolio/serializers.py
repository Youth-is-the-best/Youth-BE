from rest_framework import serializers
from .models import Portfolio, ThisIsMe, BingoComplete, OtherComplete


# 저는 이런 사람 입니다 시리얼라이저
class ThisIsMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThisIsMe
        fields = ['id', 'content']


# 달성한 빙고 시리얼라이저
class BingoCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BingoComplete
        fields = ['id', 'content']


# 다른 성과 시리얼라이저
class OtherCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherComplete
        fields = ['id', 'content']


# 포트폴리오 시리얼라이저
class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        exclude = ['user']