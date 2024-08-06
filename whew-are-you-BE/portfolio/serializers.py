from rest_framework import serializers
from .models import Portfolio, ThisIsMe, BingoComplete, OtherComplete
from datetime import datetime


class CustomDateField(serializers.DateField):
    def to_representation(self, value):
        # 출력 형식 설정
        return value.strftime('%Y.%m.%d')

    def to_internal_value(self, data):
        # 입력 형식 설정
        for date_format in ('%Y.%m.%d', '%Y-%m-%d'):
            try:
                return datetime.strptime(data, date_format).date()
            except ValueError:
                continue
        raise serializers.ValidationError("Invalid date format. Use 'YYYY.MM.DD' or 'YYYY-MM-DD'.")
    

# 저는 이런 사람 입니다 시리얼라이저
class ThisIsMeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ThisIsMe
        fields = ['id', 'content']


# 달성한 빙고 시리얼라이저
class BingoCompleteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = BingoComplete
        fields = ['id', 'content']


# 다른 성과 시리얼라이저
class OtherCompleteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    
    class Meta:
        model = OtherComplete
        fields = ['id', 'content']


# 포트폴리오 시리얼라이저
class PortfolioSerializer(serializers.ModelSerializer):
    birth = CustomDateField(required=False)
    image = serializers.ImageField(source='user.type_result.image', read_only=True, required=False)
    user_type = serializers.CharField(source='user.type_result.user_type', read_only=True, required=False)

    class Meta:
        model = Portfolio
        exclude = ['user']