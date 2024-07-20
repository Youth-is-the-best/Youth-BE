from rest_framework_simplejwt.serializers import RefreshToken
from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

# 회원가입 시리얼라이저
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, validators=[validate_password]) # 적절한 비밀번호인지 체크(너무 쉬운 비밀번호 방지)
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())]) # 이메일 중복 방지 validator
    phone_number = serializers.CharField(required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())])    # 전화번호 중복 방지 validator
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    university = serializers.CharField(required=True)
    college = serializers.CharField(required=True)
    major = serializers.CharField(required=True)
    birth = serializers.DateField(required=True)

    class Meta:
        model = CustomUser
        fields = ['password', 'username', 'email', 'first_name', 'last_name', 'university', 'college', 'major', 'birth', 'phone_number']

    def save(self, request):
        user = CustomUser.objects.create(
            username=self.validated_data['username'],
            email=self.validated_data['email'],
            phone_number=self.validated_data['phone_number'],
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            university=self.validated_data['university'],
            college=self.validated_data['college'],
            major=self.validated_data['major'],
            birth=self.validated_data['birth'],
        )

        # 비밀번호를 암호화
        user.set_password(self.validated_data['password'])
        user.save()

        return user